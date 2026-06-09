# Reference — Identidade Visual do Dashboard

> Fonte de verdade visual do dashboard jurimétrico. Espelha
> `scripts/dashboard_generator.py` e `config/identidade.json`. HTML single-file
> autocontido — dados injetados na geração, ZERO fetch/localStorage/CDN em runtime.

---

## 1. Paleta

| Token | Hex | Uso |
|---|---|---|
| bg | `#101010` | fundo da página |
| bg_card | `#181818` | cartões / painéis |
| accent (lime) | `#CCFF00` | acento, KPI central, barra de procedência |
| texto | `#F2F2F2` | corpo claro |
| texto_dim | `#8A8A8A` | rótulos secundários |
| alta | `#CCFF00` | selo confiança ALTA |
| média | `#FFB020` (âmbar) | selo MÉDIA, parcial, ajuste fático |
| baixa | `#FF4D4D` (vermelho) | selo BAIXA, improcedência |
| info | `#5AA9E6` (azul) | jurisprudencial, acordo |

## 2. Tipografia + efeitos

- **Títulos:** uppercase, sans-serif, peso 700, `letter-spacing: .04em`.
- **Corpo:** `-apple-system, "Helvetica Neue", Arial, sans-serif`.
- **Eyebrow/marca:** monospace, uppercase, `letter-spacing: .18em`, cor lime.
- **Glow:** `radial-gradient` lime sutil atrás do KPI central (`rgba(204,255,0,.14)` → transparente 60%).
- **Marca fixa:** `/// JURIMETRIA · IA COMBATIVA`.

## 3. Selos de confiança

Pílula arredondada, texto `#101010` (preto) sobre fundo da cor do nível, uppercase, peso 700:

| Selo | Cor de fundo |
|---|---|
| Confiança **ALTA** | `#CCFF00` (lime) |
| Confiança **MÉDIA** | `#FFB020` (âmbar) |
| Confiança **BAIXA** | `#FF4D4D` (vermelho) |

Mapa no gerador: `SELO_COR = {"ALTA": "#CCFF00", "MEDIA"/"MÉDIA": "#FFB020", "BAIXA": "#FF4D4D"}`.

## 4. Os 7 painéis

1. **Hero (gauge)** — gauge SVG semicircular com a faixa de confiança, selo de nível, faixa %–% e o IC. `grid-column: 1/3`.
2. **Aviso** (condicional) — se `nivel == BAIXA`, banner âmbar com o aviso de amostra rasa.
3. **Desfechos observados (DataJud)** — barras horizontais: Procedência (lime), Parcial (âmbar), Improcedência (vermelho), Acordo (azul, se houver).
4. **Amostra** — key-values: total na busca (`n_total`), com desfecho legível (`n_com_desfecho`), total na base declarado (`total_declarado_datajud`), nível de confiança.
5. **Tempo médio de tramitação** — número grande em dias.
6. **Termômetro jurisprudencial** — `A_juris` em %, com contagem favorável/desfavorável/neutro.
7. **Decomposição do número** — barras com o peso de cada fonte (empírico / jurisprudencial / ajuste fático). Cumpre R-JURI-03.

Painéis extras: **Síntese do parecer** (se houver) e **Disclaimer** fixo no rodapé. Layout em grid 2 colunas; hero/aviso/decomposição/síntese/disclaimer ocupam as 2 colunas.

## 5. Gauge SVG com faixa

Semicírculo (`viewBox 0 0 300 185`), SVG **puro** (~30 linhas) — Chart.js não tem gauge com banda nativo:

- Arco de fundo cinza `#2a2a2a` (0→1, stroke-width 22, linecap round).
- Arco da **faixa de confiança** (low→high) em lime `#CCFF00` com `stroke-opacity: 0.35` — mostra a banda de incerteza.
- Marcador (círculo lime) na posição do `centro` (P_êxito).
- Texto central: `{P}%` grande + `IC {low}–{high}%` pequeno.
- Ângulo: `π − valor·π` (0 = esquerda, 1 = direita do semicírculo).

## 6. HTML → PDF (Chrome headless)

**NÃO usar WeasyPrint** — não executa JS/SVG/glow, quebra o gauge. Usar **Chrome headless**:

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu --no-pdf-header-footer \
  --print-to-pdf=dash.pdf "file:///caminho/absoluto/dash.html"
```

- Caminho do HTML como `file://` **absoluto** (`Path.resolve().as_uri()`).
- `@page { size: A4; margin: 14mm; }` no CSS.
- Fallback: se `--no-pdf-header-footer` falhar, tentar `--print-to-pdf-no-header` (flag antiga).
- Se o Chrome não existir no path → o gerador emite só o HTML e avisa que o PDF falhou (degradação graciosa, não quebra).

---

## Args do CLI (`scripts/dashboard_generator.py`)

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/dashboard_generator.py" \
  --in resultado.json --out-html dashboard-jurimetria.html --pdf dashboard-jurimetria.pdf
```

| Flag | Default | Nota |
|---|---|---|
| `--in` | obrigatório | JSON canônico do resultado (triagem + empírico + jurisprudencia + motor + sintese_parecer + disclaimer) |
| `--out-html` | `dashboard-jurimetria.html` | saída HTML |
| `--pdf` | — | opcional; só gera PDF se passado |

O JSON de entrada espera as chaves de topo: `triagem`, `empirico`, `jurisprudencia`, `motor`, `sintese_parecer` (opcional), `disclaimer`.
