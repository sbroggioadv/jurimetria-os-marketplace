---
name: dashboard-jurimetrico
description: >
  DASHBOARD-JURIMETRICO — Monta o JSON canonico do resultado (triagem
  + empirico DataJud + jurisprudencia + motor + sintese) e gera o
  dashboard visual: HTML standalone (autocontido, sem CDN/fetch) +
  PDF via Chrome headless, na identidade #101010/#CCFF00. Explica os
  7 paineis: gauge de probabilidade com faixa de confianca, barras de
  desfecho (proc/parcial/improc/acordo), cartao da amostra com selo,
  tempo medio de tramitacao, termometro jurisprudencial, decomposicao
  do numero por fonte, e sintese do parecer + disclaimer. Salva na
  pasta local do caso (nunca iCloud). Use quando o usuario disser
  "gera o dashboard", "monta o painel", "exporta o PDF da analise",
  "quero o grafico do risco" ou quando o orquestrador encadear apos o
  parecer-jurimetrico.
---

# DASHBOARD-JURIMETRICO — Painel Visual da Jurimetria

## 1. PAPEL

Sou a skill que **monta o objeto canonico final e gera o dashboard**.
Reuno os pedacos que as skills anteriores produziram, escrevo o JSON
no schema unico e chamo o `dashboard_generator.py`, que devolve um
HTML standalone + PDF. Nao recalculo nada — apenas agrego e renderizo.

## 2. SCHEMA CANONICO QUE MONTO

Construo este objeto (1 fonte da verdade — `scripts/lib/canonical.py`)
e gravo em `resultado.json` na pasta do caso:

```json
{
  "triagem": {
    "materia": "...", "classe": 7, "classe_nome": "Procedimento Comum Civel",
    "assuntos": [{"codigo": 0, "nome": "..."}],
    "tribunal": "TJSP", "estado": "SP", "grau": "G1",
    "polo": "ativo", "tese_central": "..."
  },
  "empirico": "<saida de coleta_datajud.py>",
  "jurisprudencia": "<saida de coleta_jurisprudencia.py>",
  "motor": "<saida de motor_calculo.py>",
  "sintese_parecer": "<paragrafo da skill parecer-jurimetrico>",
  "disclaimer": "<disclaimer canonico>"
}
```

Regras de montagem:
- `empirico`, `jurisprudencia`, `motor` entram **verbatim** (a saida JSON
  de cada CLI). Nao reescrevo campos.
- `triagem` vem da `triagem-demanda`. `classe_nome` e o nome TPU
  legivel — o dashboard usa para o contexto do cabecalho.
- `sintese_parecer` e o paragrafo gerado por `parecer-jurimetrico`
  (aparece no painel "Sintese do parecer").
- Campo de etapa ausente -> deixo `null` (degradacao graciosa; o
  gerador trata com placeholders "—"). Nunca preencho com numero falso.
- O gerador usa `motor.polo_cliente`/`empirico.polo_cliente` para o
  rotulo do polo no gauge.

## 3. COMANDO DE GERACAO

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/dashboard_generator.py" \
  --in resultado.json \
  --out-html dash.html \
  --pdf dash.pdf
```

- HTML sempre gerado. PDF so se o Chrome headless existir; se falhar,
  o gerador avisa "FALHOU (Chrome headless indisponivel)" e eu entrego
  o HTML (que abre no navegador e imprime para PDF manualmente).
- O HTML e **autocontido**: SVG puro para o gauge, CSS para as barras,
  zero CDN/fetch/localStorage. Pode ser enviado por e-mail/anexo.

## 4. OS 7 PAINEIS (o que cada um mostra)

1. **Gauge de probabilidade (hero)** — SVG semicircular. Ponteiro no
   `motor.p_exito_central`; a banda lime translucida marca a `faixa`
   (`motor.faixa[0]`–`[1]`); selo de confianca colorido
   (ALTA=lime / MEDIA=ambar / BAIXA=vermelho).
2. **Desfechos observados (DataJud)** — barras horizontais:
   `taxa_procedencia`, `taxa_parcial`, `taxa_improcedencia`,
   `taxa_acordo` (se houver). Vazio -> "Sem amostra com desfecho legivel".
3. **Cartao da amostra** — `n_total`, `n_com_desfecho`,
   `total_declarado_datajud` e o nivel de confianca com a cor do selo.
   E a prova de honestidade: mostra quantos casos sustentam o numero.
4. **Tempo medio de tramitacao** — `tempo_medio_dias` em destaque.
5. **Termometro jurisprudencial** — `a_jurisprudencial` em %, com a
   contagem favoravel/desfavoravel/neutro e o `n`.
6. **Decomposicao do numero** — barras dos pesos `decomposicao.empirico`,
   `.jurisprudencial`, `.fatico`. Mostra de onde vem o percentual.
7. **Sintese do parecer + disclaimer** — o paragrafo `sintese_parecer`
   e o disclaimer canonico no rodape (faixa cinza, sempre presente).

Se `motor.aviso` existir (confianca BAIXA), o gerador insere uma faixa
de aviso ambar no topo — eu garanto que o aviso esteja no objeto.

## 5. IDENTIDADE VISUAL

`#101010` fundo / `#CCFF00` lime de marca / titulos uppercase / glow
radial sutil no hero / eyebrow "/// JURIMETRIA · IA COMBATIVA".
Selos: ALTA `#CCFF00` · MEDIA `#FFB020` · BAIXA `#FF4D4D`. Nao altero
o CSS do gerador — a identidade e fixa.

## 6. PERSISTENCIA (local, nunca iCloud)

Gravo `resultado.json`, `dash.html` e `dash.pdf` na **pasta do caso**
informada pelo usuario/orquestrador (ex.: `~/Casos/<cliente>/<caso>/`).
Append-only por consulta: cada analise vira um arquivo datado, nunca
sobrescreve a anterior. **NUNCA** salvo em pasta sincronizada por
iCloud/Dropbox/Drive (dado sensivel de caso). Se a pasta nao for
informada, pergunto antes de gravar.

## 7. INVARIANTES R-JURI (invioláveis)

- **R-JURI-01:** o gauge so renderiza com `motor` presente (p + faixa +
  IC). Sem motor, nao monto dashboard — devolvo ao orquestrador.
- **R-JURI-04:** nao invento campo. Etapa faltante = `null` -> "—" no
  painel. Numero fabricado = proibido.
- **R-JURI-05:** o painel 7 sempre carrega o disclaimer canonico:

> Estimativa probabilistica com base em dados publicos (DataJud/CNJ) e
> jurisprudencia. NAO constitui garantia de resultado. O numero
> acompanha sempre o tamanho da amostra com desfecho legivel e o
> intervalo de confianca.

## 8. PROIBICOES

1. **NUNCA** monto dashboard sem o objeto do motor (gauge ficaria vazio
   ou enganoso).
2. **NUNCA** preencho campo ausente com numero estimado — fica `null`.
3. **NUNCA** salvo em pasta sincronizada na nuvem (iCloud/Dropbox/Drive).
4. **NUNCA** edito o CSS/identidade do gerador (marca fixa).
5. **NUNCA** removo o disclaimer nem o cartao da amostra (sao a prova
   de honestidade do painel).
