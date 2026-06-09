# CLAUDE.md — plugin-jurimetria (interno do source)

> Regras internas do source. Plugin alvo: `jurimetria-os`. Família Adv-OS.
> Fonte de verdade técnica: `.planning/2026-06-09-fatos-verificados.md` (códigos TPU, API DataJud, estatística — verificados ao vivo).

## Identidade
- **Slug:** `jurimetria-os` · **Orquestrador:** `jurimetria-master` · **Onboarding:** `/start-jurimetria`
- **Source privado:** repo privado do organizador · **Marketplace público:** `jurimetria-os-marketplace`
- **Destino:** VENDA Kirvano — despersonalizado (autoria "IA Combativa"; estilo do parecer = "padrão combativo", sem identidade pessoal).
- **Natureza:** plugin **CONECTADO** (NÃO standalone) — usa DataJud ao vivo + jurisprudência (WebSearch/WebFetch nativo + Firecrawl/BD opcional). Motor Python determinístico via Bash; hook echo-only.

## Arquitetura (motor determinístico + skills)
- **Engine Python** (`scripts/lib/`): `tpu.py` (códigos verificados), `datajud_client.py` (ES + chave pública + smoke-test + search_after só @timestamp), `desfecho.py` (parser por código), `estatistica.py` (Wilson + pesos adaptativos), `canonical.py` (schema único).
- **CLIs** (`scripts/`): `coleta_datajud.py`, `coleta_jurisprudencia.py` (scorer), `motor_calculo.py`, `dashboard_generator.py` (HTML+PDF Chrome headless).
- **9 skills:** jurimetria-master, jurimetria-onboarding, triagem-demanda, coleta-datajud, coleta-jurisprudencia, motor-calculo, parecer-jurimetrico, dashboard-jurimetrico, auditoria-jurimetrica.
- **references/** na RAIZ (NÃO em skill folders — regra Cowork): datajud-api, tpu-mapeamento, modelo-estatistico, identidade-visual.
- **config/**: tribunais.json, pesos.json, identidade.json.

## CORREÇÃO CRÍTICA do PRD (anti-halucinação)
O PRD dizia "movimento 12223, complemento 3/4/5". ERRADO (verificado). Desfecho = código do MOVIMENTO → **219 procedente / 220 improcedente / 221 parcial** (filhos de 385). Acordo 466. Tudo centralizado em `scripts/lib/tpu.py` com data/fonte. O PRD também usava um nome de parecer com identidade pessoal — neutralizado para "padrão combativo".

## Invariantes R-JURI (invioláveis)
1. Número NUNCA sem n (n_com_desfecho) + IC. 2. n<30 → faixa + BAIXA + aviso. 3. Declarar peso de cada fonte (decomposição). 4. Zero fabricação de jurisprudência (3 níveis; fetch real). 5. Disclaimer fixo em toda saída.

## Validado contra DataJud REAL (2026-06-09)
Smoke-test chave pública OK; coleta TJSP classe 7/2023 (n_total 300, n_com_desfecho 187 — gap honesto); motor → dashboard HTML+PDF E2E. 2 bugs pegos ao vivo e corrigidos: `_id` no sort dá 400 (usar só @timestamp); faixa do motor agora centrada no p_exito (ponto dentro da banda).

## Regras duras da família
hooks echo-only (zero python); SKILL.md ≤11KB; description ≤1024; onboarding com botões; só SKILL.md por skill folder; audit LIMPO + check APROVADO antes do push; validate marketplace PASS.

## Persistência (D4 PRD)
Local append-only por consulta (JSON na pasta do caso), NUNCA iCloud/Dropbox.

---
**Última atualização:** 2026-06-09 — FASE 1 completa (motor validado ao vivo, 9 skills, gates verdes).
