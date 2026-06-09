#!/usr/bin/env python3
"""dashboard_generator.py — JSON canonico -> dashboard HTML standalone + PDF.

Autocontido: SVG puro (gauge com faixa de confianca) + CSS (barras). SEM
Chart.js/CDN/fetch/localStorage — dados injetados na geracao. PDF via Chrome
headless (executa o SVG/CSS fielmente; WeasyPrint nao serve).

USO:
  python3 dashboard_generator.py --in resultado.json --out-html dash.html --pdf dash.pdf
"""

from __future__ import annotations
import argparse
import html
import json
import math
import subprocess
import sys
from pathlib import Path

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

SELO_COR = {"ALTA": "#CCFF00", "MEDIA": "#FFB020", "BAIXA": "#FF4D4D",
            "MÉDIA": "#FFB020"}


def _ang(v: float) -> float:
    return math.pi - max(0.0, min(1.0, v)) * math.pi


def _pt(v: float, rad: float, cx: float = 150, cy: float = 150):
    return (cx + rad * math.cos(_ang(v)), cy - rad * math.sin(_ang(v)))


def _arc(v0: float, v1: float, rad: float) -> str:
    x0, y0 = _pt(v0, rad)
    x1, y1 = _pt(v1, rad)
    large = 1 if (v1 - v0) > 0.5 else 0
    return f"M {x0:.1f} {y0:.1f} A {rad} {rad} 0 {large} 1 {x1:.1f} {y1:.1f}"


def gauge_svg(center: float, low: float, high: float) -> str:
    r, sw = 120, 22
    mx, my = _pt(center, r)
    return f"""<svg viewBox="0 0 300 185" width="300" height="185">
  <path d="{_arc(0,1,r)}" stroke="#2a2a2a" stroke-width="{sw}" fill="none" stroke-linecap="round"/>
  <path d="{_arc(low,high,r)}" stroke="#CCFF00" stroke-opacity="0.35" stroke-width="{sw}" fill="none" stroke-linecap="round"/>
  <circle cx="{mx:.1f}" cy="{my:.1f}" r="{sw/2+4:.0f}" fill="#CCFF00" stroke="#101010" stroke-width="3"/>
  <text x="150" y="150" text-anchor="middle" font-size="44" font-weight="700" fill="#F2F2F2">{round(center*100)}%</text>
  <text x="150" y="174" text-anchor="middle" font-size="13" fill="#8A8A8A">IC {round(low*100)}–{round(high*100)}%</text>
</svg>"""


def _bar(label: str, pct: float, cor: str) -> str:
    w = max(0.0, min(100.0, pct * 100))
    return (f'<div class="barrow"><span class="blab">{html.escape(label)}</span>'
            f'<span class="btrack"><span class="bfill" style="width:{w:.1f}%;background:{cor}"></span></span>'
            f'<span class="bval">{w:.0f}%</span></div>')


def build_html(d: dict) -> str:
    motor = d.get("motor") or {}
    emp = d.get("empirico") or {}
    juris = d.get("jurisprudencia") or {}
    tri = d.get("triagem") or {}
    p = motor.get("p_exito_central") or 0.0
    faixa = motor.get("faixa") or [0, 0]
    nivel = (motor.get("nivel_confianca") or "BAIXA").upper()
    selo = SELO_COR.get(nivel, "#FF4D4D")
    decomp = motor.get("decomposicao") or {}

    titulo = html.escape(tri.get("tese_central") or tri.get("materia") or "Análise jurimétrica")
    contexto = " · ".join(filter(None, [tri.get("classe_nome") or (str(tri.get("classe")) if tri.get("classe") else None),
                                        tri.get("tribunal"), tri.get("estado")]))

    barras = ""
    if emp.get("n_com_desfecho"):
        barras += _bar("Procedência", emp.get("taxa_procedencia") or 0, "#CCFF00")
        barras += _bar("Parcial", emp.get("taxa_parcial") or 0, "#FFB020")
        barras += _bar("Improcedência", emp.get("taxa_improcedencia") or 0, "#FF4D4D")
        if emp.get("taxa_acordo"):
            barras += _bar("Acordo", emp.get("taxa_acordo") or 0, "#5AA9E6")

    # Termometro jurisprudencial
    fav = juris.get("favoravel") or 0
    desf = juris.get("desfavoravel") or 0
    neu = juris.get("neutro") or 0
    tot_j = fav + desf + neu
    a_juris = juris.get("a_jurisprudencial")
    term = (f"{round((a_juris or 0)*100)}%" if a_juris is not None else "—")

    decomp_bars = ""
    for k, lab, cor in [("empirico", "Empírico (DataJud)", "#CCFF00"),
                        ("jurisprudencial", "Jurisprudencial", "#5AA9E6"),
                        ("fatico", "Ajuste fático", "#FFB020")]:
        v = decomp.get(k) or 0
        decomp_bars += _bar(lab, abs(v), cor)

    sintese = html.escape(d.get("sintese_parecer") or "")
    disclaimer = html.escape(d.get("disclaimer") or "")
    aviso = motor.get("aviso")
    aviso_html = f'<div class="aviso">⚠️ {html.escape(aviso)}</div>' if aviso else ""

    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<title>Jurimetria — {titulo}</title>
<style>
@page {{ size: A4; margin: 14mm; }}
* {{ box-sizing: border-box; }}
body {{ background:#101010; color:#F2F2F2; font-family:-apple-system,"Helvetica Neue",Arial,sans-serif; margin:0; padding:28px; }}
.eyebrow {{ color:#CCFF00; font-size:12px; letter-spacing:.18em; text-transform:uppercase; font-family:monospace; }}
h1 {{ font-size:26px; text-transform:uppercase; letter-spacing:.04em; margin:6px 0 2px; }}
.ctx {{ color:#8A8A8A; font-size:13px; margin-bottom:18px; }}
.grid {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; }}
.card {{ background:#181818; border-radius:14px; padding:18px 20px; border:1px solid #232323; }}
.card.hero {{ grid-column:1/3; display:flex; align-items:center; gap:24px; position:relative; overflow:hidden; }}
.glow {{ position:absolute; inset:0; background:radial-gradient(circle at 30% 40%,rgba(204,255,0,.14),transparent 60%); }}
.ptit {{ color:#8A8A8A; font-size:11px; letter-spacing:.12em; text-transform:uppercase; margin-bottom:10px; }}
.big {{ font-size:40px; font-weight:700; }}
.selo {{ display:inline-block; padding:4px 12px; border-radius:99px; font-weight:700; font-size:12px; text-transform:uppercase; letter-spacing:.05em; color:#101010; }}
.barrow {{ display:flex; align-items:center; gap:10px; margin:7px 0; font-size:13px; }}
.blab {{ width:120px; color:#cfcfcf; }} .bval {{ width:42px; text-align:right; color:#8A8A8A; }}
.btrack {{ flex:1; height:12px; background:#232323; border-radius:99px; overflow:hidden; }}
.bfill {{ display:block; height:100%; border-radius:99px; }}
.kv {{ display:flex; justify-content:space-between; font-size:13px; padding:4px 0; border-bottom:1px solid #232323; }}
.kv span:last-child {{ color:#fff; font-weight:600; }}
.term {{ font-size:34px; font-weight:700; color:#CCFF00; }}
.aviso {{ grid-column:1/3; background:#2a1f00; border:1px solid #FFB020; color:#FFD479; padding:12px 16px; border-radius:10px; font-size:13px; }}
.sintese {{ grid-column:1/3; }} .sintese p {{ line-height:1.55; font-size:14px; color:#dcdcdc; white-space:pre-wrap; }}
.disclaimer {{ grid-column:1/3; color:#6f6f6f; font-size:11px; border-top:1px solid #232323; padding-top:12px; }}
</style></head><body>
<div class="eyebrow">/// JURIMETRIA · IA COMBATIVA</div>
<h1>{titulo}</h1>
<div class="ctx">{html.escape(contexto)}</div>
<div class="grid">
  <div class="card hero"><div class="glow"></div>
    <div>{gauge_svg(p, faixa[0], faixa[1])}</div>
    <div><div class="ptit">Probabilidade de êxito (polo {html.escape(emp.get("polo_cliente") or "ativo")})</div>
      <div class="selo" style="background:{selo}">Confiança {nivel}</div>
      <div style="margin-top:10px;color:#8A8A8A;font-size:13px">Faixa {round(faixa[0]*100)}%–{round(faixa[1]*100)}% (IC {html.escape(motor.get("intervalo_confianca") or "95%")})</div>
    </div>
  </div>
  {aviso_html}
  <div class="card"><div class="ptit">Desfechos observados (DataJud)</div>{barras or '<div style="color:#8A8A8A">Sem amostra com desfecho legível.</div>'}</div>
  <div class="card"><div class="ptit">Amostra</div>
    <div class="kv"><span>Total na busca</span><span>{emp.get("n_total","—")}</span></div>
    <div class="kv"><span>Com desfecho legível</span><span>{emp.get("n_com_desfecho","—")}</span></div>
    <div class="kv"><span>Total na base (declarado)</span><span>{emp.get("total_declarado_datajud","—")}</span></div>
    <div class="kv"><span>Nível de confiança</span><span style="color:{selo}">{nivel}</span></div>
  </div>
  <div class="card"><div class="ptit">Tempo médio de tramitação</div><div class="big">{emp.get("tempo_medio_dias","—")}<span style="font-size:16px;color:#8A8A8A"> dias</span></div></div>
  <div class="card"><div class="ptit">Termômetro jurisprudencial</div>
    <div class="term">{term}</div>
    <div style="color:#8A8A8A;font-size:12px;margin-top:6px">favorável · {fav} | desfavorável · {desf} | neutro · {neu} (n={tot_j})</div>
  </div>
  <div class="card" style="grid-column:1/3"><div class="ptit">Decomposição do número (peso de cada fonte)</div>{decomp_bars}</div>
  {f'<div class="card sintese" style="grid-column:1/3"><div class="ptit">Síntese do parecer</div><p>{sintese}</p></div>' if sintese else ''}
  <div class="disclaimer">{disclaimer}</div>
</div>
</body></html>"""


def gerar_pdf(html_path: Path, pdf_path: Path) -> bool:
    if not Path(CHROME).exists():
        return False
    cmd = [CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
           f"--print-to-pdf={pdf_path}", html_path.resolve().as_uri()]
    try:
        subprocess.run(cmd, check=True, capture_output=True, timeout=60)
        return pdf_path.exists()
    except Exception:
        # fallback flag antiga
        cmd[3] = "--print-to-pdf-no-header"
        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=60)
            return pdf_path.exists()
        except Exception:
            return False


def main() -> int:
    ap = argparse.ArgumentParser(description="Gera dashboard HTML + PDF da jurimetria.")
    ap.add_argument("--in", dest="infile", required=True, help="JSON canonico do resultado")
    ap.add_argument("--out-html", default="dashboard-jurimetria.html")
    ap.add_argument("--pdf", help="path do PDF (opcional)")
    args = ap.parse_args()

    d = json.loads(Path(args.infile).read_text(encoding="utf-8"))
    html_doc = build_html(d)
    out_html = Path(args.out_html)
    out_html.write_text(html_doc, encoding="utf-8")
    print(f"HTML: {out_html.resolve()}")

    if args.pdf:
        ok = gerar_pdf(out_html, Path(args.pdf))
        print(f"PDF: {'gerado em '+args.pdf if ok else 'FALHOU (Chrome headless indisponivel)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
