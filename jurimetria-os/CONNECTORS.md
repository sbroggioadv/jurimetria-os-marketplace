# CONNECTORS — jurimetria-os

Este plugin é **conectado** (usa dados ao vivo). Funciona com o que vem de fábrica no Claude Code/Cowork; integrações extras são **opcionais** (degradação graciosa).

## 1. DataJud (CNJ) — fonte empírica primária · OBRIGATÓRIA
- **O que é:** API pública do CNJ com metadados processuais (classe, assuntos, órgão, movimentos TPU). NÃO traz inteiro teor nem partes (sigilo/LGPD).
- **Chave:** pública, publicada pelo CNJ. O plugin já embute a chave pública vigente como fallback; para produção, defina a env var `DATAJUD_API_KEY`.
- **Renovação:** a chave rotaciona. Fonte de verdade: **https://datajud-wiki.cnj.jus.br/api-publica/acesso/** (⚠️ o portal antigo publica uma chave MORTA → 401). O onboarding faz smoke-test automático.
- **Como testar:** `python3 scripts/coleta_datajud.py --alias tjsp --smoke`

## 2. Jurisprudência — WebSearch + WebFetch (NATIVOS) · sempre disponíveis
- A coleta de jurisprudência usa as ferramentas nativas de busca/fetch do Claude Code. **Não exige nenhum MCP pago.** Cada citação é carimbada (validada / [VALIDAR] / impossibilidade) e só entra no parecer se confirmada por fetch real.

## 3. Opcionais (power-ups, se você tiver) — melhoram a coleta de jurisprudência
- **Firecrawl** (MCP): scraping mais robusto de portais de tribunais.
- **Bright Data** (MCP, pago): resolve captcha/bloqueio em portais difíceis.
- **Tavily / Midpage** (MCP): reforço de pesquisa jurídica.
- Se nenhum estiver presente, o plugin usa WebSearch/WebFetch e **declara cobertura jurisprudencial reduzida**, rebalanceando o peso para o empírico.

## 4. Privacidade (LGPD)
- O DataJud já omite partes/sigilosos. O plugin **não armazena dado pessoal de terceiro**. Persistência local (JSON na pasta do caso), **nunca em iCloud/Dropbox**.
