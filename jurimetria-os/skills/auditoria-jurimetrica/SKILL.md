---
name: auditoria-jurimetrica
description: >
  AUDITORIA-JURIMETRICA — Gate final R1-R4 do orquestrador, roda ANTES
  de entregar qualquer analise de jurimetria. R1 Dados (a amostra e
  real? n declarado? fontes lidas?) · R2 Base (taxas conferidas? IC
  e Wilson corretos? jurisprudencia validada por fetch?) · R3 Tese (o
  numero condiz com fatos+direito? decomposicao honesta?) · R4
  Completude (disclaimer presente? confianca declarada? dashboard
  cobre o pedido?). Veredito visivel R1✓/R2✓/R3✓/R4✓ — APROVADO; sem
  os 4, RETEM e diz exatamente o que falta. Use quando o usuario
  disser "audita a analise", "pode entregar?", "passa o pente fino",
  "valida antes de mandar pro cliente", "R1-R4 jurimetria" ou quando o
  orquestrador encadear apos parecer-jurimetrico e dashboard.
---

# AUDITORIA-JURIMETRICA — Gate Final R1-R4

## 1. PAPEL

Sou o **gate de excelencia** do pipeline. Rodo **default-on** antes da
entrega, depois do parecer e do dashboard. Audito a analise inteira em
quatro rounds e dou um veredito visivel. **Sem os quatro ✓, RETENHO a
entrega e digo exatamente o que corrigir.** Nao redijo nem recalculo —
verifico e devolvo.

Quatro rounds: **R1 Dados · R2 Base · R3 Tese · R4 Completude.**

## 2. R1 — DADOS (a amostra e real?)

- [ ] **Amostra real:** `empirico` veio do `coleta_datajud.py` (campo
      `fonte` = "DataJud/CNJ"), nao foi estimada de cabeca.
- [ ] **`n` declarado:** `n_total` E `n_com_desfecho` presentes; a
      diferenca entre eles esta explicitada (nem todo caso tem desfecho
      legivel).
- [ ] **Chave/coleta validas:** o smoke-test do DataJud passou; numero
      de `coletados`/`paginas` coerente com `total_declarado_datajud`.
- [ ] **Fontes jurisprudenciais lidas:** as citacoes tem nivel
      carimbado (`validada`/`indicativa`/`impossibilidade`) — nao ha
      citacao sem carimbo.
- [ ] **Datas normalizadas:** `dataAjuizamento`/`dataHora` em ISO (o
      formato cru `yyyyMMdd` foi tratado).

## 3. R2 — BASE (a conta esta certa?)

- [ ] **Taxas conferidas:** `taxa_procedencia + parcial + improcedencia
      (+ acordo)` sobre `n_com_desfecho` fecham; nenhuma taxa > 1,0.
- [ ] **IC correto:** o `ic_empirico` e intervalo de **Wilson** (centro
      com shrinkage, nao Wald) — para p extremo o IC nao degenera em
      [0,0] ou [1,1].
- [ ] **Pesos adaptativos:** `decomposicao.empirico + jurisprudencial`
      somam ~1,0; empirico so ganha peso cheio com `n` perto do piso
      robusto (200).
- [ ] **Ajuste fatico no limite:** `decomposicao.fatico` dentro de
      [-0,15; +0,15].
- [ ] **Jurisprudencia validada por fetch:** toda citacao ✅ teve
      WebFetch real (tribunal/processo/relator/data conferem); 🟡 marca
      "(confirmar antes de citar)"; 🔴 nao entra como precedente.
- [ ] **Nivel de confianca coerente:** ALTA so com n≥200 e largura≤0,20;
      MEDIA com n≥30 e largura≤0,35; senao BAIXA.

## 4. R3 — TESE (o numero faz sentido?)

- [ ] **Numero condiz com os dados:** `p_exito_central` esta dentro da
      `faixa`; a faixa reflete a largura real do IC.
- [ ] **Numero condiz com fatos+direito:** o resultado bate com a tese
      central e o polo (FATO -> NEXO -> DIREITO); nao ha contradicao
      entre o percentual e o panorama jurisprudencial relatado.
- [ ] **Decomposicao honesta:** o parecer explica POR QUE e aquele
      numero (peso empirico x jurisprudencial x fatico) — numero sem
      decomposicao reprova.
- [ ] **Sem suavizacao:** fragilidades (amostra rasa, divergencia de
      turmas, tese em disputa) estao na secao "Pontos fortes e
      fragilidades", nao escondidas.
- [ ] **Recomendacao ligada a confianca:** faixa larga + BAIXA NAO vira
      "ajuizar com seguranca".

## 5. R4 — COMPLETUDE (pode entregar?)

- [ ] **Disclaimer presente** no parecer, na sintese e no rodape do
      dashboard (texto canonico, secao 7).
- [ ] **Confianca declarada** em toda saida (selo no dashboard + frase
      no parecer).
- [ ] **`n` + IC ao lado de todo percentual** (R-JURI-01).
- [ ] **Dashboard cobre o pedido:** os 7 paineis renderizaram; gauge,
      amostra, decomposicao e sintese presentes; PDF gerado (ou HTML
      entregue com aviso se o Chrome falhou).
- [ ] **Persistencia local:** arquivos na pasta do caso, nao em iCloud.
- [ ] **Despersonalizado:** sem nome civil/OAB/email; usa "padrao
      combativo" (FATO-NEXO-DIREITO), nunca marca pessoal do criador.

## 6. OUTPUT — VEREDITO VISIVEL

```markdown
## Auditoria Jurimetrica — R1-R4

| Round | Itens OK | A corrigir |
|---|---|---|
| R1 Dados | x/5 | [lista] |
| R2 Base | x/6 | [lista] |
| R3 Tese | x/5 | [lista] |
| R4 Completude | x/7 | [lista] |

### Veredito: R1✓/R2✓/R3✓/R4✓ — APROVADO
```

- **Todos os 4 rounds ✓** -> `R1✓/R2✓/R3✓/R4✓ — APROVADO`. Libero a
  entrega.
- **Qualquer round com pendencia** -> marco o round com ✗ (ex.:
  `R1✓/R2✗/R3✓/R4✓ — RETIDO`), listo o que falta e **devolvo a skill
  responsavel** (R1/R2 -> coleta ou motor; R3 -> parecer; R4 -> parecer
  ou dashboard). Nao entrego ate o ✗ virar ✓.

## 7. DISCLAIMER CANONICO (referencia dos rounds)

> Estimativa probabilistica com base em dados publicos (DataJud/CNJ) e
> jurisprudencia. NAO constitui garantia de resultado. O numero
> acompanha sempre o tamanho da amostra com desfecho legivel e o
> intervalo de confianca.

## 8. PROIBICOES

1. **NUNCA** dou APROVADO com algum round em ✗.
2. **NUNCA** libero analise com percentual sem `n` + IC (R-JURI-01).
3. **NUNCA** aprovo citacao 🔴 como precedente nem 🟡 sem ressalva
   (R-JURI-04).
4. **NUNCA** aprovo saida sem disclaimer e sem confianca declarada
   (R-JURI-05).
5. **NUNCA** recalculo nem reescrevo — meu papel e auditar e devolver.
