---
description: Onboarding do plugin jurimetria-os. Configura o advogado usuario (nome, tom) e testa a chave publica do DataJud (smoke-test), alem de checar MCPs opcionais (Firecrawl/Bright Data/Tavily/Midpage). Use na primeira vez, ou quando a coleta do DataJud falhar (chave rotacionada). Aciona a skill jurimetria-onboarding com botoes clicaveis (AskUserQuestion).
---

# /start-jurimetria

Configuracao inicial do plugin **jurimetria-os**.

Aciona a skill **`jurimetria-onboarding`**, que vai:

- Perguntar nome do advogado e tom de voz do parecer (botoes nas escolhas fechadas).
- **Testar a chave do DataJud:** `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/coleta_datajud.py" --alias tjsp --smoke`. Se der 401, a chave rotacionou — renovar em https://datajud-wiki.cnj.jus.br/api-publica/acesso/ e definir a env `DATAJUD_API_KEY`.
- Checar quais MCPs opcionais de jurisprudencia estao disponiveis (Firecrawl/Bright Data/Tavily/Midpage). Nenhum e obrigatorio — WebSearch/WebFetch nativos bastam.

A configuracao fica salva localmente na persona do usuario (fora do plugin distribuido).
