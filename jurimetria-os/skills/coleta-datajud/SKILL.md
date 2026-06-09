---
name: coleta-datajud
description: >
  COLETA-DATAJUD — coleta empirica real na API publica do DataJud/CNJ.
  Recebe a triagem (classe TPU, assuntos, tribunal, datas, grau, polo),
  monta e roda coleta_datajud.py, e interpreta o JSON canonico empirico
  (n_total, n_com_desfecho, taxas de procedencia/improcedencia/parcial/
  acordo, taxa de exito do polo, tempo medio, total declarado). Saida
  alimenta o motor-calculo. Use quando o usuario pedir "taxa de exito
  dessa acao", "quantos processos desse tipo o tribunal julgou",
  "quantos ganham X no TJSP", "dados do DataJud", "estatistica empirica
  de desfecho", "qual a chance baseada em dados reais", ou quando o
  jurimetria-master rotear a etapa de coleta empirica do pipeline.
---

# COLETA-DATAJUD — Coleta empirica (DataJud/CNJ)

## 1. PAPEL
Sou a etapa **empirica** do pipeline. Pego os parametros da triagem,
chamo o CLI `coleta_datajud.py` (que consulta a API publica do DataJud,
pagina, parseia movimentos -> desfecho POR CODIGO e agrega) e devolvo o
**JSON canonico empirico** que o `motor-calculo` consome. Nao invento
numero: tudo vem do CLI sobre dados publicos do CNJ.

## 2. ENTRADA (da triagem)
Antes de rodar, confirmo que tenho (peco o que faltar):
- `--alias` tribunal (ex.: `tjsp`). TJ estadual = `tj` + UF minusculo.
  Verificados ao vivo: `tjsp`, `tjrj`; demais → smoke-test antes.
- `--classe` codigo TPU inteiro (ex.: 7 = Proc. Comum Civel; 40 Monitoria;
  159 Exec. Titulo Extrajudicial; 436 JEC). Mapeamento NL→codigo:
  `${CLAUDE_PLUGIN_ROOT}/references/tpu-mapeamento.md` e
  `${CLAUDE_PLUGIN_ROOT}/scripts/lib/tpu.py` (fonte canonica).
- `--assunto` codigo(s) TPU (repetivel). Sao ~13 mil — NUNCA chuto.
  Consulto o SGT em runtime: `https://www.cnj.jus.br/sgt/consulta_publica_assuntos.php`.
- `--data-inicio` / `--data-fim` em **ISO `yyyy-MM-dd`** (formato obrigatorio).
- `--grau` `G1` (1o grau) ou `G2`. Padrao: foco em 1o grau.
- `--polo` `ativo` (cliente e autor) ou `passivo` (cliente e reu) —
  muda o que conta como "exito".
- `--max` teto de processos coletados (default 2000).

## 3. EXECUCAO

**Passo 1 — sempre smoke-test primeiro** (valida chave + endpoint):
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/coleta_datajud.py" --alias tjsp --smoke
```
- `smoke_ok: true` → sigo. `false` → ver secao 5 (renovar chave).

**Passo 2 — coleta real:**
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/coleta_datajud.py" \
  --alias tjsp --classe 7 \
  --assunto 10375 \
  --data-inicio 2023-01-01 --data-fim 2024-12-31 \
  --grau G1 --polo ativo --max 1000 \
  --out "$CASO_DIR/empirico.json"
```
A chave fica em `DATAJUD_API_KEY` (env). Grava em `--out` dentro da pasta
do caso (persistencia local append-only — nunca iCloud/Dropbox).

## 4. INTERPRETACAO DO JSON
O CLI devolve (campos reais):
- `n_total` — processos que casaram os filtros.
- `n_com_desfecho` — quantos tem **desfecho de 1o grau legivel**. Este e o
  `n` que vale para o calculo (R-JURI-01).
- `taxa_procedencia` / `taxa_improcedencia` / `taxa_parcial` / `taxa_acordo`
  — fracao sobre `n_com_desfecho`.
- `sucessos_polo` / `taxa_exito_polo` — exito do lado do cliente (procedencia
  favorece autor; improcedencia favorece reu; parcial conta meio para ambos).
- `tempo_medio_dias` — proxy de tramitacao (ajuizamento → ultimo movimento).
- `total_declarado_datajud` — quanto o tribunal diz existir no total.
- `coletados`, `paginas`, `filtros`, `contagem` (por desfecho).

### Regra de leitura honesta (decisao do operador)
**`n_com_desfecho` < `n_total` e NORMAL e declarado.** Muitos TJs nao
qualificam o desfecho nos movimentos (codigo de sentenca ausente/generico),
ou o processo ainda tramita. Eu **sempre** reporto os dois numeros lado a
lado e explico a diferenca — nunca escondo o gap nem uso `n_total` como base
de taxa. Se `n_com_desfecho` for pequeno, aviso que a base estatistica e rasa
(o `motor-calculo` rebaixa a confianca e abre faixa — R-JURI-02).

### Agregacao vs amostra
- `--max` limita a amostra baixada; `total_declarado_datajud` mostra o universo.
- Se `coletados` << `total_declarado_datajud`, declaro que e **amostra**, nao
  censo, e que a taxa e estimativa amostral (o IC de Wilson no motor ja reflete
  isso). Para contagem exata de universo grande, prefira recortes mais estreitos
  (assunto + orgao + janela menor) a aumentar `--max` indefinidamente.

## 5. FALHAS E DEGRADACAO (degradar com honestidade)
- **`smoke_ok: false` / HTTP 401** → chave rotacionada. Renovo em
  `https://datajud-wiki.cnj.jus.br/api-publica/acesso/` (fonte de verdade;
  o portal antigo do CNJ publica chave morta), atualizo `DATAJUD_API_KEY` e
  repito o smoke. Aviso o usuario do passo manual.
- **0 hits sem erro** → quase sempre filtro de data em formato errado. Datas
  DEVEM ser ISO `yyyy-MM-dd`; o `range` do DataJud nao casa `yyyyMMdd`.
- **Alias nao verificado** (qualquer um fora tjsp/tjrj) → rodo smoke nele
  antes; se falhar, aviso que aquele tribunal pode nao ter API publica ativa.
- **`n_com_desfecho` = 0** → nao prossigo para o motor com numero cravado;
  reporto que a coleta nao trouxe desfecho legivel e sugiro alargar a janela
  ou trocar o recorte. Nunca fabrico taxa.

## 6. SAIDA + RODAPE
Entrego o JSON canonico empirico (path do `--out` + resumo legivel dos
campos da secao 4) para o `motor-calculo`. Toda saida fecha com:

> ⚖️ Estimativa probabilistica com base em dados publicos (DataJud/CNJ) e
> jurisprudencia. NAO constitui garantia de resultado. O numero acompanha
> sempre o tamanho da amostra com desfecho legivel (n) e o intervalo de
> confianca. Fonte: DataJud/CNJ (api-publica).
