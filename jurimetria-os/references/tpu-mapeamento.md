# Reference — Mapeamento TPU (Tabelas Processuais Unificadas / CNJ)

> Fonte de verdade dos códigos de desfecho. SGT/CNJ (consulta pública de
> movimentos/classes, tabela v26/05/2026) + planilhas oficiais CNJ/TST.
> Verificado jun/2026. Espelha `scripts/lib/tpu.py`.

---

## 🔴 CORREÇÃO CRÍTICA — o PRD original ERROU

O PRD afirmava: *"movimento 12223 Sentença, complemento 3 = Procedência / 4 = Improcedência / 5 = Procedência em parte"*. **ISSO ESTÁ ERRADO.**

O desfecho de um processo é o **CÓDIGO DO MOVIMENTO** (219/220/221), **NÃO** um complemento 3/4/5. Não existe complemento 3/4/5 de resultado. O complemento auxiliar de resultado, quando usado, tem códigos **7462/7463/7464** (seção 3 abaixo), e só para movimentos genéricos.

**Regra de ouro (anti-halucinação):** decidir desfecho SEMPRE por **código inteiro**, NUNCA por texto. Os nomes da TPU têm placeholders (`Julgado(s)...`) e acentuação variável entre tribunais.

---

## 1. Movimentos de desfecho (1º grau)

Árvore TPU: `1 Magistrado → 193 Julgamento → 385 Com resolução do mérito → {219, 220, 221, ...}` / `→ 218 Sem resolução do mérito → {...}`.

| Código | Desfecho (parser) | Nome oficial |
|---|---|---|
| **219** | `PROCEDENTE` | Julgado(s) procedente(s) o(s) pedido(s) |
| **220** | `IMPROCEDENTE` | Julgado(s) improcedente(s) o(s) pedido(s) |
| **221** | `PARCIALMENTE_PROCEDENTE` | Julgado(s) procedente(s) em parte |
| 50103 | `IMPROCEDENTE` | Liminarmente improcedente (art. 332 CPC) |
| 471 | `EXTINTO_MERITO` | Decadência/prescrição (art. 487, II) |
| 50094 | (ver complemento §3) | Julgamento antecipado parcial (art. 356) |

### Autocomposição (mérito — art. 487, III)

| Código | Desfecho |
|---|---|
| 466 | `ACORDO_HOMOLOGADO` (homologada a transação) |
| 11795 | `RECONHECIMENTO_PROCEDENCIA` |
| 455 | `RENUNCIA_HOMOLOGADA` |
| 377 / 14099 | `ACORDO_HOMOLOGADO` (acordo em execução/cumprimento) |

### Sem resolução do mérito (pais 218 / 456)

| Código | Desfecho |
|---|---|
| 454 | `EXTINTO_SEM_MERITO` (indeferimento da inicial) |
| 459 | `EXTINTO_SEM_MERITO` (ausência de pressupostos) |
| 460 | `EXTINTO_SEM_MERITO` (perempção/litispendência/coisa julgada) |
| 461 | `EXTINTO_SEM_MERITO` (ausência de legitimidade/interesse) |
| 457 | `EXTINTO_SEM_MERITO` (negligência) |
| 458 | `EXTINTO_SEM_MERITO` (abandono) |
| 463 | `DESISTENCIA_HOMOLOGADA` |
| 196 | `EXECUCAO_EXTINTA` (extinta a execução/cumprimento) |

## 2. Movimentos RECURSAIS (instância separada — NÃO contar como 1º grau)

| Código | Desfecho recursal |
|---|---|
| 237 | `RECURSO_PROVIDO` |
| 238 | `RECURSO_PARCIALMENTE_PROVIDO` |
| 239 | `RECURSO_NAO_PROVIDO` |
| 235 | `RECURSO_NAO_CONHECIDO` |
| 236 | `RECURSO_NEGADO_SEGUIMENTO` (sem mérito) |

O parser separa recursal de 1º grau — não mistura os dois na taxa de procedência.

## 3. Complemento auxiliar "Resultado do julgamento"

Usado SÓ quando o movimento é genérico (ex.: 50094 — julgamento antecipado parcial). O `valor`/`codigo` do complemento é numérico:

| Código complemento | Desfecho |
|---|---|
| 7462 | `PROCEDENTE` |
| 7463 | `IMPROCEDENTE` |
| 7464 | `PARCIALMENTE_PROCEDENTE` |

`MOVIMENTOS_COM_COMPLEMENTO_RESULTADO = {50094}` no parser.

## 4. Flag (não é desfecho)

- **848** — Transitado em julgado. É **flag** separada (`transitado: true`), nunca conta como desfecho.

## 5. Regra do parser (`desfecho.py`)

1. Decidir SEMPRE por **código inteiro**, nunca por texto.
2. Ordenar movimentos por `dataHora` **decrescente**; o **mais recente** que bater em `DESFECHO_POR_MOVIMENTO` vence (1º grau).
3. Recursal é registrado separado (`desfecho_recursal`).
4. Se movimento genérico (50094) → ler `complementosTabelados` para achar 7462/7463/7464.
5. Se **nada bate** → `INDEFINIDO` (não chutar). Processos `INDEFINIDO` entram em `n_total` mas **não** em `n_com_desfecho` (transparência — R-JURI-01).
6. **Êxito depende do polo:** procedência favorece o **autor** (polo ativo); para o **réu** (polo passivo) inverte-se PROCEDENTE↔IMPROCEDENTE. Parcial conta como meio-êxito para ambos.

## 6. Classes TPU comuns (parametrização CNJ 2024)

| Código | Classe |
|---|---|
| 7 | Procedimento Comum Cível |
| 22 | Procedimento Sumário |
| 40 | Monitória |
| 81 | Busca e Apreensão em Alienação Fiduciária |
| 93 | Despejo por Falta de Pagamento |
| 436 | Procedimento do Juizado Especial Cível (JEC) |
| 156 | Cumprimento de Sentença |
| 157 | Cumprimento Provisório de Sentença |
| 159 | Execução de Título Extrajudicial |
| 1116 | Execução Fiscal |
| 1118 | Embargos à Execução Fiscal |

**Execução de Título Extrajudicial** tem variantes por revisão da TPU: aceitar o conjunto `{159, 990, 12154}`.

## 7. Assuntos — NÃO hardcodar (~13 mil entradas)

A tabela de assuntos tem ~13.000 entradas. **Não hardcodar.** Consultar o SGT em runtime ou perguntar na triagem:

- Assuntos: <https://www.cnj.jus.br/sgt/consulta_publica_assuntos.php>
- Classes: <https://www.cnj.jus.br/sgt/consulta_publica_classes.php>
- Movimentos: <https://www.cnj.jus.br/sgt/consulta_publica_movimentos.php>

⚠️ **Classe ≠ assunto ≠ movimento são tabelas SEPARADAS.** O mesmo número significa coisas diferentes entre elas (ex.: código 7 é "Procedimento Comum Cível" como classe, mas outra coisa como assunto). Nunca cruzar tabelas por número.

## 8. Proveniência (anti-halucinação)

- Versão da tabela: **2026-05-26**
- Fonte: SGT/CNJ + planilhas oficiais CNJ/TST
- Extraído em: 2026-06-09
- Aviso: códigos podem mudar em novas versões da TPU. Reconfirmar no SGT antes de cada release. Centralizados em `scripts/lib/tpu.py` (`TPU_META`) com data + fonte.
