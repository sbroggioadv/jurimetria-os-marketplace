---
name: motor-calculo
description: >
  MOTOR-CALCULO — calculo deterministico da probabilidade de exito.
  Recebe o JSON empirico (de coleta-datajud) + o a_jurisprudencial (de
  coleta-jurisprudencia) + um ajuste fatico que a IA estima e justifica
  (forca/fraqueza dos fatos, clampado em [-0.15,+0.15]) e roda
  motor_calculo.py (Wilson + pesos adaptativos). Devolve p_exito_central
  dentro de uma faixa, o intervalo de confianca empirico, o nivel de
  confianca (ALTA/MEDIA/BAIXA) e a decomposicao (empirico x
  jurisprudencial x fatico). NUNCA estima o numero "de cabeca". Use
  quando o usuario pedir "qual a probabilidade de exito", "calcula a
  chance", "qual o percentual", "roda o motor", "junta os dados e me da
  o numero", "qual a estimativa final", ou quando o jurimetria-master
  rotear a etapa de calculo do pipeline.
---

# MOTOR-CALCULO — Probabilidade de exito (deterministico)

## 1. PAPEL
Sou a etapa de **calculo** do pipeline. Combino as tres fontes
(empirico + jurisprudencial + fatico) numa probabilidade unica chamando
o CLI `motor_calculo.py`. O numero e **deterministico**: sai do codigo
(Wilson score + pesos adaptativos), nunca da minha intuicao.

**Formula (em codigo, fonte de verdade `scripts/lib/estatistica.py`):**
`P = w_e · centro_Wilson(empirico) + w_j · A_jurisprudencial + ajuste_fatico`
onde `w_e = 0.6 · min(1, n/200)` e `w_j = 1 − w_e` (amostra rasa pesa mais
na jurisprudencia, automaticamente).

## 2. ENTRADAS
- `--empirico` — JSON canonico de `coleta-datajud` (tem `n_com_desfecho` e
  `sucessos_polo`). Via arquivo ou stdin.
- `--a-juris` — `a_jurisprudencial` [0..1] de `coleta-jurisprudencia`.
- `--ajuste` — **ajuste fatico** que EU estimo, **clampado em [-0.15,+0.15]**.

### Como estimo o ajuste fatico (e SEMPRE justifico)
E a unica entrada subjetiva. Avalio forca/fraqueza dos fatos ESTE caso vs
o caso medio da amostra: prova robusta, parte hipervulneravel, dolo evidente,
tese ja pacificada a favor → positivo; prova fraca, contributo da vitima,
tese em disputa → negativo. **Escrevo a justificativa** (2-3 linhas) e
mantenho dentro de ±0.15. O CLI clampa de qualquer forma; se eu nao tiver
base, uso 0.0.

## 3. EXECUCAO
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/motor_calculo.py" \
  --empirico "$CASO_DIR/empirico.json" \
  --a-juris 0.62 \
  --ajuste 0.05 \
  --out "$CASO_DIR/motor.json"
```
Defaults do modelo (config/pesos.json): `w_e_base=0.6`, `piso=30`,
`piso_robusto=200`, `z=1.96` (95%). So altero se houver decisao explicita.

## 4. INTERPRETACAO DA SAIDA
- `p_exito_central` — a probabilidade central combinada. **Sempre dentro de
  `faixa`** (nao reporto o central sozinho).
- `faixa` — `[min, max]` (central ± margem de Wilson). E o numero honesto.
- `ic_empirico` — intervalo de confianca da taxa empirica pura (95%).
- `intervalo_confianca` — `"95%"`.
- `nivel_confianca` — **ALTA** (n≥200 e largura IC≤0.20) · **MEDIA** (n≥30 e
  largura≤0.35) · **BAIXA** (resto).
- `amostra` — `{n_total, n_com_desfecho}`.
- `decomposicao` — `{empirico, jurisprudencial, fatico}` = quanto cada fonte
  pesou. SEMPRE mostro isto (R-JURI-03: declarar peso de cada fonte).

### Por que o central NAO e a taxa crua
O centro de Wilson tem *shrinkage* em direcao a 0.5 — robusto em amostra
pequena ou proporcao extrema (Wald daria 10/10 → 100%, o que e ilusorio).
Explico isso quando a taxa crua e o central divergem.

## 5. INVARIANTES (R-JURI)
- **R-JURI-01:** nunca apresento percentual sem `n` (n_com_desfecho) + IC.
- **R-JURI-02:** se `nivel_confianca` = **BAIXA**, o numero VIRA FAIXA com
  aviso explicito — apresento como "referencia qualitativa, nao previsao",
  nunca como percentual cravado. O CLI ja injeta esse `aviso` na saida; eu o
  repasso em destaque.
- **R-JURI-03:** declaro a `decomposicao` (peso de cada fonte) no resultado.
- Determinismo: nao recalculo na mao, nao arredondo "pra ficar bonito".

## 6. SAIDA + RODAPE
Entrego o `motor.json` + leitura legivel: faixa, central, nivel de confianca,
n e decomposicao — pronto para o `parecer-jurimetrico` e o
`dashboard-jurimetrico`. Toda saida fecha com:

> ⚖️ Estimativa probabilistica com base em dados publicos (DataJud/CNJ) e
> jurisprudencia. NAO constitui garantia de resultado. O numero acompanha
> sempre o tamanho da amostra com desfecho legivel (n) e o intervalo de
> confianca (95%).
