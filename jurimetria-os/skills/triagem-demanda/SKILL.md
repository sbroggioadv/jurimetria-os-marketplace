---
name: triagem-demanda
description: >
  TRIAGEM-DEMANDA — Normaliza um relato de caso em linguagem natural num
  objeto estruturado para o motor de jurimetria: matéria, rito, classe
  TPU, assuntos TPU, tribunal (alias DataJud), estado, grau, polo do
  cliente e tese central. Mapeia linguagem natural → código TPU (cita
  references/tpu-mapeamento.md). PERGUNTA o que faltar — nunca supõe em
  silêncio. Use quando o usuário descrever um caso para análise
  jurimétrica, disser "quero a probabilidade dessa ação", "analisa esse
  caso", "vale a pena ajuizar", "qual a classe disso", "que código TPU é
  essa ação", ou quando o orquestrador precisar dos filtros de busca
  antes de coletar dados no DataJud.
---

> **🖱️ Escolhas = botões:** em campos de **lista fechada** (polo ativo/passivo, grau G1/G2, escolha entre classes candidatas) use **AskUserQuestion** (máx. 4 botões). Texto livre (tese, descrição) segue digitado.

# TRIAGEM-DEMANDA — Normalização do Caso

## 1. PAPEL

Transformo o relato do advogado num **objeto de triagem** que o pipeline consome para montar a query do DataJud. Mapeio a linguagem natural para os códigos TPU corretos e **pergunto** o que faltar — nunca chuto um código em silêncio (anti-halucinação).

## 2. CAMPOS A EXTRAIR

| Campo | O que é | De onde |
|---|---|---|
| `materia` | área (cível, consumidor, bancário, trabalhista...) | relato |
| `rito` | comum / sumário / JEC / execução / monitória | relato + valor da causa |
| `classe` (código TPU) | ex.: 7 = Procedimento Comum Cível | ref tpu-mapeamento §6 |
| `classe_nome` | nome legível da classe | ref tpu-mapeamento §6 |
| `assuntos` (códigos TPU) | ex.: dano moral, revisão de contrato | **consultar SGT** (§4) |
| `tribunal` (alias DataJud) | tjsp, tjrj, stj, tst... | UF/justiça do caso |
| `estado` | UF | relato |
| `grau` | G1 (1º grau) / G2 (recurso) | relato |
| `polo_cliente` | ativo (autor) / passivo (réu) | **pergunta sempre** |
| `tese_central` | a tese jurídica em 1 frase | relato |
| `periodo` | janela de ajuizamento (data-início/fim ISO) | sugiro 2 anos recentes |

## 3. MAPA NL → CLASSE TPU (cita `references/tpu-mapeamento.md`)

Não decoro a tabela inteira aqui — uso a referência. Atalhos comuns:

| Linguagem do advogado | Classe TPU |
|---|---|
| "ação de indenização", "danos morais", "comum cível" | 7 — Procedimento Comum Cível |
| "monitória", "cobrança por cheque/nota" | 40 — Monitória |
| "busca e apreensão do carro", "alienação fiduciária" | 81 — Busca e Apreensão |
| "despejo por falta de pagamento" | 93 — Despejo |
| "juizado", "JEC", "pequena causa" | 436 — JEC |
| "cumprimento de sentença" | 156 |
| "execução de título extrajudicial", "execução de CCB/contrato" | {159, 990, 12154} |
| "execução fiscal" | 1116 · "embargos à execução fiscal" | 1118 |

Se o relato casar com **mais de uma** classe candidata → mostrar as candidatas em **botões** e deixar o advogado escolher. Se não casar com nenhuma → consultar o SGT de classes (§4) ou perguntar.

## 4. ASSUNTOS TPU — consultar, NUNCA hardcodar

A tabela de assuntos tem **~13 mil entradas** (ref tpu-mapeamento §7). Não invento código de assunto. Opções:
1. Consultar o SGT em runtime: <https://www.cnj.jus.br/sgt/consulta_publica_assuntos.php>
2. Ou perguntar ao advogado o código/nome do assunto.
3. Ou rodar a coleta **só por classe** (sem assunto) e avisar que a amostra é mais ampla.

⚠️ Classe ≠ assunto ≠ movimento são tabelas separadas — o mesmo número significa coisas diferentes. Nunca cruzar por número.

## 5. POLO DO CLIENTE — sempre perguntar (define "êxito")

O que conta como êxito **depende do polo**:
- **Ativo (autor):** êxito = procedência (+ parcial como meio-êxito).
- **Passivo (réu):** êxito = improcedência (+ parcial como meio-êxito).

Se não estiver claro no relato, **perguntar com botões** (Autor / Réu). Nunca assumir.

## 6. O QUE PERGUNTAR (só o que faltar)

Checklist antes de liberar para o pipeline. Faltando qualquer um → pergunto:
- [ ] matéria + tese central
- [ ] classe TPU (ou candidatas resolvidas)
- [ ] tribunal/alias + estado + grau
- [ ] **polo do cliente** (sempre)
- [ ] período (sugiro últimos 2 anos se omitido)
- [ ] assuntos (ou aceitar busca só por classe, declarando)

## 7. SAÍDA — objeto de triagem (para o orquestrador)

```yaml
triagem:
  materia: "consumidor / cobrança indevida"
  rito: "comum"
  classe: 7
  classe_nome: "Procedimento Comum Cível"
  assuntos: [7698]          # vazio se buscou só por classe (declarar)
  tribunal: "tjsp"          # alias DataJud
  estado: "SP"
  grau: "G1"
  polo_cliente: "ativo"     # ativo = autor | passivo = réu
  tese_central: "Cobrança indevida gera repetição em dobro (CDC 42 §ún)."
  periodo: { data_inicio: "2023-01-01", data_fim: "2024-12-31" }
  observacoes: "Assunto não fixado — busca por classe; amostra mais ampla."
```

Esse objeto vira os filtros do `coleta_datajud.py` (`--classe`, `--assunto`, `--alias`, `--grau`, `--polo`, `--data-inicio/-fim`).

## 8. PROIBIÇÕES

1. Nunca inventar código TPU (classe/assunto/movimento) — consultar a referência/SGT ou perguntar.
2. Nunca assumir o polo do cliente em silêncio.
3. Nunca cruzar tabelas de classe/assunto/movimento por número.
4. Nunca prosseguir com campos obrigatórios faltando — perguntar.
5. Declarar quando a busca for só por classe (sem assunto) — afeta o `n`.

## 💡 Próximo passo

Com a triagem pronta, o `jurimetria-master` dispara o pipeline: `coleta-datajud` → `motor-calculo` → (completo) `coleta-jurisprudencia` + `parecer-jurimetrico` + `auditoria-jurimetrica` + `dashboard-jurimetrico`.
