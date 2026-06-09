---
name: jurimetria-onboarding
description: >
  JURIMETRIA-ONBOARDING — Comando `/start-jurimetria`. Configura a persona
  do advogado operador (nome, OAB, UF, tribunais, áreas, tom de voz),
  testa a chave da API DataJud (smoke-test) e checa MCPs opcionais de
  coleta de jurisprudência (Firecrawl/Bright Data/Tavily). Persiste em
  `<cwd>/jurimetria/persona.md`. AVISO LGPD: orienta a NÃO criar a pasta
  dentro de iCloud/Google Drive/Dropbox/OneDrive (dados de caso não vivem
  em sync de nuvem). Use SEMPRE na primeira sessão do plugin OU quando o
  usuário disser "configurar", "primeira vez", "start jurimetria",
  "/start-jurimetria", "testar chave DataJud", "trocar tom de voz",
  "adicionar tribunal", "atualizar OAB".
---

> **🖱️ Escolhas = botões:** em campos de **lista fechada** (áreas, tom de voz, atualizar/recriar, sim/não) use **AskUserQuestion** para mostrar **botões clicáveis** (máx. 4 por pergunta; se houver mais, divida em 2). **Texto livre** (nome, OAB, cidade) segue como pergunta digitada.

# JURIMETRIA-ONBOARDING — Configuração + Smoke-test

## 1. ESCOPO

Prepara o plugin para uso:
1. Configura a **persona** do operador → `<cwd>/jurimetria/persona.md`.
2. **Smoke-test** da chave DataJud (verifica que a API responde antes do 1º uso).
3. **Checa MCPs opcionais** de coleta de jurisprudência (degradação graciosa).

Pré-requisito das demais skills. Sem persona + chave validada, o orquestrador roda esta primeiro.

## 2. QUANDO RODAR

- Primeira sessão (persona.md não existe).
- Comando `/start-jurimetria`.
- "configurar plugin", "testar chave DataJud", "trocar tom", "adicionar tribunal".

## 3. FLUXO

### Passo 1 — Aviso LGPD (CRÍTICO, bloqueador)

```
⚠️ AVISO DE PRIVACIDADE (LGPD)

A pasta `jurimetria/` guardará sua configuração + memórias de análise
(dados empíricos de processos, possivelmente ligados a casos reais).

NÃO crie esta pasta dentro de:
- iCloud Drive (~/Library/Mobile Documents/...)
- Google Drive / Dropbox / OneDrive
- Pastas pessoais do sistema (Documents, Desktop, Downloads)

Recomendado: pasta local fora de qualquer sync de nuvem.
Sua sessão está em: <cwd atual>
```

Se o cwd contém `iCloud`, `Google Drive`, `Dropbox`, `OneDrive`, `Mobile Documents`, `CloudDocs` → **PARAR** e pedir mudança de cwd.

### Passo 2 — Coletar persona (UMA pergunta por vez)

1. Nome profissional (como aparece em pareceres)? *(texto livre)*
2. Número OAB (formato UF Número, ex.: SP 123.456)? *(texto livre)*
3. UF de inscrição? *(texto livre)*
4. Tribunais que você acompanha? (ex.: TJSP, TJRJ, TRF3, TST, STJ) *(texto livre, lista)*
5. Áreas que você pratica? *(BOTÕES — máx. 4 por pergunta; divida se preciso: cível / consumidor / bancário / trabalhista / tributário / previdenciário / família / empresarial)*
6. Tom de voz dos pareceres? *(BOTÕES: técnico-direto · didático · formal · consultivo)*
7. Escritório (opcional)? · Cidade-base? *(texto livre)*

### Passo 3 — Smoke-test da chave DataJud

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/coleta_datajud.py" --alias tjsp --smoke
```

Interpretar a saída JSON (`smoke_ok`):
- **`true`** → "✅ Chave DataJud OK — a API respondeu. Pronto para coletar."
- **`false` com 401** → "🔴 Chave INVÁLIDA/ROTACIONADA. Renove em https://datajud-wiki.cnj.jus.br/api-publica/acesso/ e exporte em `DATAJUD_API_KEY`." A chave embutida é pública mas pode rotacionar; o portal antigo do CNJ publica uma chave **morta**.
- outro erro → mostrar a mensagem e sugerir checar conexão/alias.

> Como definir a env (orientar o operador, não executar por ele):
> `export DATAJUD_API_KEY="<chave da wiki>"`

### Passo 4 — Checar MCPs opcionais (jurisprudência)

A coleta de jurisprudência funciona com **WebSearch + WebFetch nativos** (todo Claude Code tem). MCPs abaixo são **opcionais** — melhoram cobertura, mas o plugin não depende deles:

- **Firecrawl** — motor primário recomendado (scraping robusto).
- **Bright Data / Tavily / Midpage** — fallbacks opcionais.

Detectar quais estão disponíveis na sessão e informar:
```
Coleta de jurisprudência: WebSearch/WebFetch nativos ✅ (sempre)
MCPs opcionais detectados: [Firecrawl ✅ | Bright Data — | Tavily —]
Sem MCP, a cobertura é menor mas o plugin funciona (degradação graciosa).
```
Detalhes em `${CLAUDE_PLUGIN_ROOT}/CONNECTORS.md`.

### Passo 5 — Confirmação + persistir

Mostrar resumo (tabela) e perguntar (BOTÃO sim/não): "Posso salvar em `<cwd>/jurimetria/persona.md`?"

Conteúdo do `persona.md`:

```markdown
# Persona — jurimetria-os

> Configuração do operador. NÃO commitar em repo público. NÃO incluir
> dados de processo de cliente aqui.

## Identidade
- **Nome:** [nome]
- **OAB:** [UF + número]
- **UF:** [UF]
- **Escritório:** [nome ou "advocacia individual"]
- **Cidade-base:** [cidade]

## Atuação
- **Tribunais:** [lista CSV — aliases DataJud: tjsp, tjrj, stj...]
- **Áreas:** [lista CSV]

## Preferências
- **Tom de voz:** [técnico-direto | didático | formal | consultivo]

## Ambiente
- **DATAJUD_API_KEY:** [configurada via env? sim/não — smoke-test em YYYY-MM-DD: OK/FALHOU]
- **MCPs jurisprudência:** [Firecrawl/BD/Tavily detectados]

## Auditoria
- **Configurado em:** [YYYY-MM-DD]
- **Última atualização:** [YYYY-MM-DD]
- **Versão plugin:** v0.1.0
```

### Passo 6 — Confirmação final

```
✅ Persona em `<cwd>/jurimetria/persona.md` · Chave DataJud: [OK/pendente]

Próximos passos:
- `/jurimetria` — análise livre (orquestrador roteia)
- "qual a probabilidade de êxito de [tese] no [tribunal]?"

Lembre: adicione `jurimetria/` ao .gitignore do seu projeto.
```

## 4. ATUALIZAÇÃO DE PERSONA EXISTENTE

Se `persona.md` já existe, perguntar (BOTÕES) o que atualizar: Tribunais · Áreas/Tom · OAB/nome · Re-testar chave DataJud · Resetar tudo · Cancelar. Aplicar a mudança e atualizar `Última atualização`.

## 5. OUTPUT (resumo)

```yaml
persona:
  configurada: true
  arquivo: "<cwd>/jurimetria/persona.md"
  datajud_chave: "<OK | pendente | rotacionada>"
  mcps_juris: [firecrawl?, bright_data?, tavily?]
  status: pronto_para_uso
```

## 6. PROIBIÇÕES

1. Não salvar persona em pasta sync (LGPD bloqueador).
2. Não coletar dados de cliente (CPF, nº de processo) — persona é da OPERAÇÃO, não do caso.
3. Não enviar telemetria — tudo fica em disco local.
4. Não perguntar tudo de uma vez (UMA por vez).
5. Não prosseguir com a chave sem rodar o smoke-test.

## 💡 Próximos passos opcionais

| Próximo passo | Comando | Plugin necessário |
|---|---|---|
| Configurar persona da operação jurídica | `/start` | ia-combativa-adv-os |
| Configurar persona de cálculo judicial | `/start-calculos` | calculosjudiciais-adv-os |

> Cada plugin Adv-OS tem onboarding próprio com persona local em `<cwd>/<plugin>/`.
