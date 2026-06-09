#!/usr/bin/env python3
"""coleta_jurisprudencia.py — scorer deterministico do alinhamento jurisprudencial.

NAO faz scraping aqui (isso e a skill coleta-jurisprudencia, que usa WebSearch/
WebFetch/Firecrawl e CARIMBA o nivel de cada citacao). Este CLI recebe as
citacoes ja coletadas+carimbadas pela skill e calcula A_jurisprudencial [0..1]
de forma determinista, alem de estruturar o JSON canonico.

REGRA ANTI-FABRICACAO: so contam citacoes com nivel 'validada' no score base;
'indicativa' [VALIDAR] entra com meio-peso; 'impossibilidade' nao conta.

ENTRADA (stdin ou --in): JSON
  { "citacoes": [ {"tribunal","processo","relator","data","alinhamento","nivel"} ] }
  alinhamento in {FAVORAVEL, DESFAVORAVEL, NEUTRO}; nivel in {validada, indicativa, impossibilidade}

SAIDA: JSON canonico de jurisprudencia (favoravel/desfavoravel/neutro, n_validada,
       n_indicativa, a_jurisprudencial, citacoes[]).
"""

from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

PESO_NIVEL = {"validada": 1.0, "indicativa": 0.5, "impossibilidade": 0.0}


def score(citacoes: list[dict]) -> dict:
    fav = desf = neu = 0.0
    n_val = n_ind = 0
    for c in citacoes:
        peso = PESO_NIVEL.get((c.get("nivel") or "").lower(), 0.0)
        if peso == 0.0:
            continue
        if c.get("nivel", "").lower() == "validada":
            n_val += 1
        elif c.get("nivel", "").lower() == "indicativa":
            n_ind += 1
        al = (c.get("alinhamento") or "").upper()
        if al == "FAVORAVEL":
            fav += peso
        elif al == "DESFAVORAVEL":
            desf += peso
        else:
            neu += peso

    base = fav + desf  # neutro nao puxa pra nenhum lado
    # A_jurisprudencial: fracao favoravel entre os direcionais; 0.5 se nao ha base.
    a = round(fav / base, 4) if base > 0 else 0.5
    return {
        "favoravel": round(fav, 2), "desfavoravel": round(desf, 2), "neutro": round(neu, 2),
        "n_validada": n_val, "n_indicativa": n_ind,
        "a_jurisprudencial": a,
        "cobertura": "PLENA" if n_val >= 5 else ("PARCIAL" if n_val + n_ind >= 3 else "RASA"),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Scorer de alinhamento jurisprudencial.")
    ap.add_argument("--in", dest="infile", help="JSON de citacoes (default: stdin)")
    ap.add_argument("--out")
    args = ap.parse_args()

    raw = Path(args.infile).read_text(encoding="utf-8") if args.infile else sys.stdin.read()
    data = json.loads(raw)
    citacoes = data.get("citacoes", [])
    res = score(citacoes)
    res["citacoes"] = citacoes
    res["fonte"] = "WebSearch/WebFetch + Firecrawl (Bright Data/Tavily/Midpage opcionais)"
    res["aviso"] = ("Cobertura RASA/PARCIAL rebalanceia o peso para o empirico. "
                    "Citacoes 'indicativa' [VALIDAR] exigem confirmacao por fetch real "
                    "antes de entrar no parecer.")

    out = json.dumps(res, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(out, encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
