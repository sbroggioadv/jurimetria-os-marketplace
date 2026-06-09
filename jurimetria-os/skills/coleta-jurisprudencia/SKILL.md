---
name: coleta-jurisprudencia
description: >
  COLETA-JURISPRUDENCIA — busca, classifica e CARIMBA julgados reais
  sobre a tese, sem fabricar nada. Usa WebSearch + WebFetch nativos
  (e Firecrawl/Bright Data/Tavily/Midpage SE disponiveis) para achar
  acordaos do tribunal-alvo e das cortes superiores; classifica o
  alinhamento (FAVORAVEL/DESFAVORAVEL/NEUTRO) e o nivel de cada citacao
  (validada / [VALIDAR] indicativa / impossibilidade), monta o
  citacoes.json e roda coleta_jurisprudencia.py para obter o
  A_jurisprudencial [0..1]. Declara cobertura PLENA/PARCIAL/RASA. Use
  quando o usuario pedir "o que os tribunais decidem sobre essa tese",
  "jurisprudencia sobre X", "como o STJ/TJ ve essa tese", "panorama
  jurisprudencial", "alinhamento jurisprudencial", ou quando o
  jurimetria-master rotear a etapa de coleta jurisprudencial.
---

# COLETA-JURISPRUDENCIA — Panorama jurisprudencial (anti-fabricacao)

## 1. PAPEL
Sou a etapa **jurisprudencial** do pipeline. Acho julgados REAIS sobre a
tese, classifico o alinhamento de cada um, **carimbo o nivel de confianca
de cada citacao** e rodo o scorer `coleta_jurisprudencia.py` para devolver
o `a_jurisprudencial` [0..1] que o `motor-calculo` consome.

**REGRA ABSOLUTA (R-JURI-04): ZERO fabricacao.** Nunca invento numero de
processo, relator, data ou ementa. Se nao confirmei por fetch real, a
citacao nao recebe selo de validada.

## 2. BUSCA (motores, em ordem de preferencia)
1. **WebSearch + WebFetch nativos** — sempre disponiveis; sao o piso.
2. **Firecrawl** (`firecrawl_search` / `firecrawl_scrape`) — motor
   principal quando instalado (melhor extracao de ementa).
3. **Bright Data / Tavily / Midpage** — opcionais; uso se presentes.

Se nenhum opcional existir, os nativos bastam (degradacao graciosa — nao
exijo `.mcp.json`). Busco no **tribunal-alvo** (ex.: TJSP) E nas **cortes
superiores** (STJ; STF quando ha tese constitucional/repercussao geral).
Fontes: sites oficiais dos tribunais, jusbrasil, JusBrasil, repositorios de
acordaos. Priorizo julgados recentes e a tese exata da triagem.

## 3. CLASSIFICACAO DE ALINHAMENTO
Para cada julgado encontrado, classifico em relacao a tese do CLIENTE:
- **FAVORAVEL** — sustenta a tese (puxa A_juris para cima).
- **DESFAVORAVEL** — contraria a tese.
- **NEUTRO** — tangencia, distingue ou nao decide o ponto (nao puxa lado).

## 4. CARIMBO DE NIVEL (o coracao da anti-halucinacao)
Cada citacao recebe UM nivel:
- **`validada`** — o WebFetch/scrape REAL na URL retornou sucesso E a
  pagina contem a ementa + o numero do processo que estou citando. So este
  nivel entra com peso cheio (1.0) no score.
- **`indicativa`** — encontrei o julgado em snippet/indice mas NAO confirmei
  ementa+numero na integra. Marco a citacao com **`[VALIDAR]`**; entra com
  meio-peso (0.5) e exige confirmacao antes de ir para o parecer.
- **`impossibilidade`** — nao consegui localizar/abrir a fonte. Nao conta
  (peso 0.0). Registro como lacuna, nao como dado.

Nunca promovo um `indicativa` a `validada` sem o fetch real bem-sucedido.

## 5. MONTAGEM + EXECUCAO
Monto o `citacoes.json` (formato exato que o CLI espera):
```json
{
  "citacoes": [
    {"tribunal": "STJ", "processo": "REsp 1.111.111/SP", "relator": "Min. Fulano",
     "data": "2024-03-10", "alinhamento": "FAVORAVEL", "nivel": "validada"},
    {"tribunal": "TJSP", "processo": "AC 2222222-22...", "relator": "Des. Beltrano",
     "data": "2023-11-02", "alinhamento": "DESFAVORAVEL", "nivel": "indicativa"}
  ]
}
```
Rodo o scorer determinista:
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/coleta_jurisprudencia.py" \
  --in "$CASO_DIR/citacoes.json" --out "$CASO_DIR/juris.json"
```

## 6. INTERPRETACAO DA SAIDA
O CLI devolve:
- `a_jurisprudencial` [0..1] — fracao favoravel entre os direcionais
  (FAVORAVEL/DESFAVORAVEL); 0.5 se nao ha base direcional. Este e o valor
  que passo ao `motor-calculo` como `--a-juris`.
- `favoravel` / `desfavoravel` / `neutro` — pesos somados.
- `n_validada` / `n_indicativa` — contagem por nivel.
- `cobertura` — **PLENA** (n_validada >= 5) · **PARCIAL** (validada+indicativa
  >= 3) · **RASA** (menos que isso).

## 7. COBERTURA E REBALANCEAMENTO (honestidade)
Declaro sempre a cobertura. **Cobertura baixa (RASA/PARCIAL) rebalanceia o
peso para o empirico** — eu sinalizo isso explicitamente, porque o
`a_jurisprudencial` derivado de pouca base e fragil. Citacoes `[VALIDAR]`
(indicativa) NAO entram no parecer final sem confirmacao por fetch real.
Se a busca falhar de vez, reporto cobertura RASA com `a_jurisprudencial`
neutro (0.5) e aviso que o numero final apoiou-se quase so no empirico.

## 8. RODAPE
Toda saida fecha com:

> ⚖️ Estimativa probabilistica com base em dados publicos (DataJud/CNJ) e
> jurisprudencia. NAO constitui garantia de resultado. Citacoes marcadas
> [VALIDAR] exigem confirmacao na integra antes de uso em peca/parecer.
> Fonte: WebSearch/WebFetch + Firecrawl (Bright Data/Tavily/Midpage opcionais).
