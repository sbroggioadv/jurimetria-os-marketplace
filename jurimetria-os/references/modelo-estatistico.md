# Reference — Modelo Estatístico da Jurimetria

> Fonte de verdade do motor de cálculo. Código testado numericamente (doctests)
> em jun/2026. Espelha `scripts/lib/estatistica.py`. Determinístico, zero
> dependências externas (só stdlib `math`). Nenhum número de saída sem intervalo
> de confiança associado (anti-halucinação).

---

## 1. Wilson score interval (por que > Wald)

Intervalo de confiança de uma proporção. **Sem continuity correction.** `z = 1.96` para 95% (Z_SCORES: 0.90→1.645, 0.95→1.96, 0.99→2.576).

```
p̂      = sucessos / n
z²      = z·z
denom   = 1 + z²/n
centro  = (p̂ + z²/2n) / denom
margem  = (z/denom) · √( p̂(1−p̂)/n + z²/4n² )
IC      = [centro − margem, centro + margem]   (clampado em [0,1])
```

**O centro NÃO é p̂** — é p̂ com *shrinkage* em direção a 0.5. Isso torna o estimador robusto em proporção extrema e amostra pequena.

**Por que > Wald (intervalo normal):** o Wald degenera em proporção extrema:
- 10/10 (100%) → Wald dá `[1,1]` (intervalo nulo, falso); Wilson dá `[0.72, 1.0]`.
- 0/10 (0%) → Wald dá `[0,0]` (falso); Wilson dá `[0, 0.28]`.

### Exemplos numéricos verificados (doctests)

| sucessos/n | IC Wilson (95%) |
|---|---|
| 7/10 | `[0.40, 0.89]` |
| 0/10 | `[0.00, 0.28]` |
| 10/10 | `[0.72, 1.00]` |

## 2. Pesos adaptativos (empírico × jurisprudencial)

Quanto menor a amostra, menos peso o empírico merece. Rampa contínua e monotônica, com `w_e + w_j = 1`:

```
fator = min(1, n_com_desfecho / piso_robusto)
w_e   = w_e_base · fator
w_j   = 1 − w_e
```

Defaults: `w_e_base = 0.6`, `piso_robusto = 200`, `piso = 30`.

| n | w_e | w_j |
|---|---|---|
| 0 | 0.00 | 1.00 (só jurisprudência) |
| 100 | 0.30 | 0.70 |
| 200+ | 0.60 | 0.40 |

Com amostra rasa, o número é dominado pela jurisprudência (e declarado como tal na decomposição — R-JURI-03).

## 3. Nível de confiança (2 variáveis: volume E precisão)

Classifica por `n` **E** largura do IC (`ic_high − ic_low`):

| Nível | Condição |
|---|---|
| **ALTA** | `n ≥ 200` **E** largura ≤ 0.20 |
| **MÉDIA** | `n ≥ 30` **E** largura ≤ 0.35 |
| **BAIXA** | caso contrário |

Exemplos verificados: `(n=10, larg=0.495)→BAIXA`; `(n=100, larg=0.192)→MEDIA`; `(n=250, larg=0.15)→ALTA`.

> Selos: ALTA = lime `#CCFF00`, MÉDIA = âmbar `#FFB020`, BAIXA = vermelho `#FF4D4D`.

## 4. Fórmula final de P_êxito

```
T_emp = centro de Wilson (já com shrinkage)
P = w_e · T_emp + w_j · A_juris + ajuste_fático
```

- `A_juris` ∈ [0,1] — alinhamento jurisprudencial (fração favorável entre as citações direcionais; vem de `coleta-jurisprudencia`).
- `ajuste_fático` ∈ **[−0.15, +0.15]** (clampado) — força/fraqueza dos fatos do caso concreto (input qualitativo da IA).
- `P` clampado em [0,1].

### Faixa do número final

```
margem = largura_IC / 2
faixa  = [ P − margem , P + margem ]   (clampado [0,1])
```

A faixa mantém o ponto P dentro da banda; a largura reflete a incerteza amostral **real** (Wilson empírico). Amostra rasa → faixa larga → nível BAIXA → o número vira **referência qualitativa**, nunca previsão cravada (R-JURI-02).

### Decomposição obrigatória (R-JURI-03)

Toda saída declara o peso de cada fonte:

```json
"decomposicao": { "empirico": 0.30, "jurisprudencial": 0.70, "fatico": 0.05 }
```

## 5. Exemplo numérico completo (end-to-end)

Caso: 70 sucessos em 100 processos com desfecho, A_juris = 0.65, ajuste = +0.05.

```
T_emp (Wilson centro de 70/100) ≈ 0.694 ; IC ≈ [0.60, 0.78] ; largura ≈ 0.18
pesos (n=100): w_e = 0.30, w_j = 0.70
P = 0.30·0.694 + 0.70·0.65 + 0.05 ≈ 0.713  → 71%
faixa = 0.713 ± 0.09 ≈ [0.62, 0.80]
nível: n≥30 e largura(0.18)≤0.35 → MÉDIA
```

Saída: **71% (faixa 62–80%), confiança MÉDIA, decomposição empírico 0.30 / juris 0.70 / fático 0.05**, com disclaimer fixo.

---

## Args do CLI (`scripts/motor_calculo.py`)

```bash
# empírico via arquivo + alinhamento juris + ajuste fático
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/motor_calculo.py" \
  --empirico empirico.json --a-juris 0.65 --ajuste 0.05 --out motor.json

# empírico via stdin (pipe da coleta)
cat empirico.json | python3 "${CLAUDE_PLUGIN_ROOT}/scripts/motor_calculo.py" --a-juris 0.65
```

| Flag | Default | Nota |
|---|---|---|
| `--empirico` | stdin | JSON canônico de `coleta_datajud.py` |
| `--a-juris` | 0.5 | alinhamento jurisprudencial [0..1] |
| `--ajuste` | 0.0 | ajuste fático [−0.15..0.15] (clampado) |
| `--w-e-base` | 0.6 | peso-base do empírico |
| `--piso` | 30 | piso para MÉDIA |
| `--piso-robusto` | 200 | piso para ALTA / 100% peso empírico |
| `--out` | — | grava JSON |

Saída inclui: `p_exito_central`, `faixa`, `ic_empirico`, `intervalo_confianca` ("95%"), `nivel_confianca`, `decomposicao`, `aviso` (se BAIXA) e `disclaimer` fixo.
