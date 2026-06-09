# Reference — API Pública DataJud (CNJ)

> Fonte de verdade técnica do cliente DataJud. Verificado ao vivo (curl HTTP 200)
> em jun/2026. Espelha `scripts/lib/datajud_client.py` — código que contraria
> isto está errado. O cliente Python usa só stdlib (`urllib`), zero dependências.

---

## 1. Endpoint

```
POST https://api-publica.datajud.cnj.jus.br/api_publica_{alias}/_search
Content-Type: application/json
Authorization: APIKey <chave>
```

É um Elasticsearch exposto. O body é uma query ES (`bool`/`term`/`range`/`sort`).

## 2. Autenticação + chave

- Header **`Authorization: APIKey <chave>`** (literal — a palavra `APIKey`, espaço, chave).
- Chave **PÚBLICA** verificada ao vivo (HTTP 200) em 2026-06-09:
  ```
  cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw==
  ```
- **Guardar em env `DATAJUD_API_KEY`.** O cliente faz `os.environ.get("DATAJUD_API_KEY", DEFAULT_PUBLIC_KEY)` — se a env existe, ela vence; senão usa a default embutida.
- **Fonte de verdade para renovação:** <https://datajud-wiki.cnj.jus.br/api-publica/acesso/>
- ⚠️ **PEGADINHA:** o portal antigo do CNJ publica uma chave **MORTA** (retorna 401). Use SEMPRE a wiki acima. **Sempre rodar smoke-test antes de confiar** na chave (`coleta_datajud.py --alias tjsp --smoke`).
- Auth inválida → HTTP **401** `security_exception`. O cliente detecta `401` e devolve "CHAVE INVALIDA/ROTACIONADA — renove em <wiki>".

## 3. Aliases por tribunal

`api_publica_{alias}` onde `{alias}` é:

| Alias | Tribunal | Status |
|---|---|---|
| `tjsp`, `tjrj` | TJ-SP, TJ-RJ | ✅ verificado |
| `tj` + UF (`tjmg`, `tjrs`, `tjba`...) | demais TJs | 🟡 confirmar via smoke-test |
| `stj` | STJ | 🟡 smoke-test |
| `tst` | TST | 🟡 smoke-test |
| `trf1`..`trf6` | TRFs | 🟡 smoke-test |
| `trt1`..`trt24` | TRTs | 🟡 smoke-test |
| STF | — | pode **não** ter alias público |

**Regra:** antes de coletar de um alias novo, smoke-test (`match_all` size:0). Se falhar, não chutar — declarar indisponibilidade.

## 4. Query: bool term + range

- Filtros numéricos via `term` (campos: `classe.codigo`, `assuntos.codigo`, `orgaoJulgador.codigo`).
- Filtro de data via `range` em `dataAjuizamento`.
- Sempre `track_total_hits: true` (sem isso `hits.total.value` **satura em 10000**).
- `sort` é obrigatório para paginar.

```json
{
  "size": 100,
  "track_total_hits": true,
  "query": { "bool": {
    "must":   [ {"term": {"classe.codigo": 7}}, {"term": {"assuntos.codigo": 7698}} ],
    "filter": [ {"term": {"grau": "G1"}},
                {"range": {"dataAjuizamento": {"gte": "2023-01-01", "lte": "2024-12-31"}}} ]
  }},
  "sort": [ {"@timestamp": {"order": "asc"}} ]
}
```

### ⚠️ Pegadinha CRÍTICA do `dataAjuizamento` (ISO)

O MESMO campo `dataAjuizamento` aparece em **2 formatos**: ISO (`2024-01-26T...`) e cru (`20210202175107`). O `range` **só casa com ISO / `yyyy-MM-dd`**. Filtrar em `yyyyMMdd` → **0 hits SEM erro** (falha silenciosa). Sempre passar datas como `yyyy-MM-dd`. A saída é normalizada para ISO no parser (`normalizar_data`).

## 5. Paginação: `search_after` (sort SÓ `@timestamp` — NÃO `_id`)

- Janela máxima `from+size` = **10.000**; acima → erro.
- Acima disso, usar **`search_after`** com o `sort` do último hit da página.
- **`sort` = SÓ `[{"@timestamp":{"order":"asc"}}]`.** O cluster do DataJud **proíbe fielddata em `_id`** → usar `_id` como tie-breaker dá **HTTP 400**. (Isso contraria intuições antigas de tie-breaker; aqui é assim.)
- Loop: repetir POST com `search_after` = `hits[-1].sort` até `hits.hits` vir vazio (ou página menor que `page_size`).

```
page = POST(query)              # 1ª página
while page.hits.hits:
    sources += page.hits.hits[]._source
    sa = page.hits.hits[-1].sort
    page = POST(query + {"search_after": sa})
```

## 6. Agregação > paginação (para contar desfecho)

Para apenas **contar** desfechos, `terms` sobre `movimentos.codigo` com `size:0` é mais barato que baixar todos os processos. (O CLI atual baixa `_source` e parseia no cliente — necessário para tempo de tramitação e desfecho "mais recente vence"; agregação é otimização opcional.)

## 7. Estrutura da resposta

- `hits.total.value` (+ `relation`; use `track_total_hits` para count exato).
- `hits.hits[]._source.{...}`:

```
numeroProcesso
classe        { codigo, nome }
assuntos      [ { codigo, nome } ]          # SEMPRE array
orgaoJulgador { codigo, nome }
tribunal, grau ("G1"/"G2"), dataAjuizamento
movimentos    [ { codigo, nome, dataHora,
                  complementosTabelados [ { codigo, valor, nome, descricao } ] } ]
```

## 8. Pegadinhas do parser (todas observadas ao vivo)

1. **`dataAjuizamento` 2 formatos** no mesmo campo (ISO + cru `yyyyMMddHHmmss`). `range` só casa com ISO. Normalizar saída para ISO.
2. **`movimentos` pode ESTAR AUSENTE** → `source.get("movimentos", [])` (nunca indexar direto).
3. `complementosTabelados` é **opcional** dentro de cada movimento; `valor`/`codigo` é id numérico, **não** texto.
4. `orgaoJulgador.codigo` é **STRING** dentro de `movimentos[]` (`"10440"`) mas **INT** na raiz (`9533`). Cast com cuidado.
5. `assuntos` é **SEMPRE array**.
6. Filtrar por `grau` ("G1"/"G2") — **o mesmo processo aparece em graus diferentes** (`_id` = `TJSP_G1_...` vs `TJSP_G2_...`). Não dupla-contar 1º grau com 2º grau.
7. `hits.total.value` **satura em 10000** sem `track_total_hits: true`.
8. Auth inválida → **401** `security_exception`.

---

## Args do CLI (`scripts/coleta_datajud.py`)

```bash
# Smoke-test da chave/endpoint (rápido, size:0 match_all)
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/coleta_datajud.py" --alias tjsp --smoke

# Coleta real -> JSON canônico empírico em stdout (--out grava arquivo)
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/coleta_datajud.py" \
  --alias tjsp --classe 7 --assunto 7698 \
  --data-inicio 2023-01-01 --data-fim 2024-12-31 \
  --grau G1 --polo ativo --max 500 --out empirico.json
```

| Flag | Tipo | Nota |
|---|---|---|
| `--alias` | obrigatório | tjsp, tjrj, stj... |
| `--classe` | int | código TPU da classe |
| `--assunto` | int (repetível) | `--assunto 7698 --assunto 9985` |
| `--orgao` | int | código do órgão julgador |
| `--data-inicio` / `--data-fim` | ISO `yyyy-MM-dd` | NUNCA `yyyyMMdd` |
| `--grau` | G1 / G2 | filtro de instância |
| `--polo` | ativo / passivo | define o que é "êxito" |
| `--max` | int (default 2000) | teto de processos coletados |
| `--smoke` | flag | só testa a chave |
| `--out` | path | grava o JSON |

Saída canônica inclui: `n_total`, `n_com_desfecho`, `taxa_procedencia/improcedencia/parcial/acordo`, `sucessos_polo`, `taxa_exito_polo`, `tempo_medio_dias`, `total_declarado_datajud`, `paginas`, `filtros`, `fonte`.
