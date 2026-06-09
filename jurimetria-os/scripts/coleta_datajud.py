#!/usr/bin/env python3
"""coleta_datajud.py — CLI: filtros -> JSON canonico de dados empiricos.

Consulta a API publica do DataJud, pagina, parseia movimentos -> desfechos,
e devolve a contagem com n_total / n_com_desfecho / taxas + tempo medio.

USO:
  # smoke-test da chave/endpoint
  python3 coleta_datajud.py --alias tjsp --smoke

  # coleta real (ex.: Procedimento Comum Civel no TJSP, 2023-2024)
  python3 coleta_datajud.py --alias tjsp --classe 7 --data-inicio 2023-01-01 \\
      --data-fim 2024-12-31 --polo ativo --max 500

SAIDA: JSON canonico (empirico) em stdout. --out grava em arquivo.
"""

from __future__ import annotations
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import datajud_client as dj  # noqa: E402
from lib import desfecho  # noqa: E402


def _parse_iso(v: str | None):
    v = dj.normalizar_data(v)
    if not v:
        return None
    try:
        return datetime.strptime(v, "%Y-%m-%d")
    except ValueError:
        return None


def tempo_medio_dias(sources: list[dict]) -> float | None:
    """Media de dias entre ajuizamento e o movimento mais recente (proxy de tramitacao)."""
    durs = []
    for s in sources:
        ini = _parse_iso(s.get("dataAjuizamento"))
        movs = s.get("movimentos") or []
        if not ini or not movs:
            continue
        datas = [m.get("dataHora", "")[:10] for m in movs if m.get("dataHora")]
        datas = [_parse_iso(d) for d in datas]
        datas = [d for d in datas if d]
        if not datas:
            continue
        fim = max(datas)
        delta = (fim - ini).days
        if delta >= 0:
            durs.append(delta)
    if not durs:
        return None
    return round(sum(durs) / len(durs), 1)


def main() -> int:
    ap = argparse.ArgumentParser(description="Coleta empirica DataJud -> JSON canonico.")
    ap.add_argument("--alias", required=True, help="ex.: tjsp, tjrj, stj")
    ap.add_argument("--classe", type=int, help="codigo TPU da classe (ex.: 7)")
    ap.add_argument("--assunto", type=int, action="append", help="codigo TPU de assunto (repetivel)")
    ap.add_argument("--orgao", type=int, help="codigo do orgao julgador")
    ap.add_argument("--data-inicio", help="ISO yyyy-MM-dd")
    ap.add_argument("--data-fim", help="ISO yyyy-MM-dd")
    ap.add_argument("--grau", help="G1 / G2")
    ap.add_argument("--polo", default="ativo", choices=["ativo", "passivo"])
    ap.add_argument("--max", type=int, default=2000, dest="maxp")
    ap.add_argument("--smoke", action="store_true", help="so testa a chave/endpoint")
    ap.add_argument("--out", help="grava JSON em arquivo")
    args = ap.parse_args()

    if args.smoke:
        ok, msg = dj.smoke_test(args.alias)
        print(json.dumps({"smoke_ok": ok, "mensagem": msg,
                          "fonte_chave": dj.WIKI_ACESSO}, ensure_ascii=False, indent=2))
        return 0 if ok else 1

    query = dj.montar_query(classe=args.classe, assuntos=args.assunto, orgao=args.orgao,
                            data_inicio=args.data_inicio, data_fim=args.data_fim,
                            grau=args.grau)
    col = dj.coletar(args.alias, query, max_processos=args.maxp)
    agg = desfecho.agregar(col["sources"], polo_cliente=args.polo)
    agg["tempo_medio_dias"] = tempo_medio_dias(col["sources"])
    agg["total_declarado_datajud"] = col["total_declarado"]
    agg["coletados"] = len(col["sources"])
    agg["paginas"] = col["paginas"]
    agg["filtros"] = {"alias": args.alias, "classe": args.classe,
                      "assuntos": args.assunto, "orgao": args.orgao,
                      "data_inicio": args.data_inicio, "data_fim": args.data_fim,
                      "grau": args.grau}
    agg["fonte"] = "DataJud/CNJ (api-publica)"

    out = json.dumps(agg, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(out, encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
