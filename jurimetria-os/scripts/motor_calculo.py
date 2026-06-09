#!/usr/bin/env python3
"""motor_calculo.py — CLI: empirico + alinhamento jurisprudencial -> objeto do motor.

Deterministico. Aplica Wilson + pesos adaptativos (lib/estatistica.py) e devolve
o formato §6.4 do PRD. NUNCA estima "de cabeca".

USO:
  python3 motor_calculo.py --empirico empirico.json --a-juris 0.6 --ajuste 0.05
  # ou empirico via stdin:
  cat empirico.json | python3 motor_calculo.py --a-juris 0.6
"""

from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import estatistica, canonical  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="Motor de calculo da jurimetria.")
    ap.add_argument("--empirico", help="JSON canonico de coleta_datajud (default: stdin)")
    ap.add_argument("--a-juris", type=float, default=0.5,
                    help="alinhamento jurisprudencial [0..1] (de coleta-jurisprudencia)")
    ap.add_argument("--ajuste", type=float, default=0.0,
                    help="ajuste fatico [-0.15..0.15] (IA, forca/fraqueza dos fatos)")
    ap.add_argument("--w-e-base", type=float, default=0.6)
    ap.add_argument("--piso", type=int, default=30)
    ap.add_argument("--piso-robusto", type=int, default=200)
    ap.add_argument("--out")
    args = ap.parse_args()

    raw = Path(args.empirico).read_text(encoding="utf-8") if args.empirico else sys.stdin.read()
    emp = json.loads(raw)

    n = emp.get("n_com_desfecho") or 0
    sucessos = emp.get("sucessos_polo")
    if sucessos is None:
        # fallback: deriva de taxa_exito_polo * n
        tx = emp.get("taxa_exito_polo") or 0.0
        sucessos = tx * n
    sucessos = int(round(sucessos))

    p = estatistica.calcular_p_exito(
        n_com_desfecho=n, sucessos=sucessos, a_jurisprudencial=args.a_juris,
        ajuste_fatico_raw=args.ajuste, w_e_base=args.w_e_base,
        piso=args.piso, piso_robusto=args.piso_robusto)

    saida = canonical.saida_motor(p, emp)
    saida["fontes"] = {
        "datajud": True,
        "a_jurisprudencial": args.a_juris,
        "ajuste_fatico": p["decomposicao"]["fatico"],
    }
    # R-JURI-02: amostra rasa -> aviso explicito
    if p["nivel_confianca"] == "BAIXA":
        saida["aviso"] = ("Amostra com desfecho legivel insuficiente (n=%d). O numero "
                          "e uma FAIXA de baixa confianca — use como referencia "
                          "qualitativa, nao como previsao." % n)
    saida["disclaimer"] = canonical.DISCLAIMER

    out = json.dumps(saida, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(out, encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
