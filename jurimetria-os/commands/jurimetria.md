---
description: Ponto de entrada do plugin jurimetria-os. Aciona o orquestrador jurimetria-master para rodar o pipeline de jurimetria preditiva (triagem da demanda -> coleta DataJud + jurisprudencia -> motor de calculo -> parecer -> auditoria R1-R4 -> dashboard). Use para estimar probabilidade de exito, risco do processo, ou viabilidade de uma demanda com base em dados.
---

# /jurimetria

Voce acionou o plugin **jurimetria-os** (jurimetria preditiva com DataJud + jurisprudencia).

Use a skill **`jurimetria-master`** (orquestrador). Pipeline:

1. **Triagem** (`triagem-demanda`) — extrai materia/classe/assunto/tribunal/polo/tese.
2. **Coleta empirica** (`coleta-datajud`) — DataJud (API CNJ) -> desfechos + amostra.
3. **Coleta jurisprudencial** (`coleta-jurisprudencia`) — julgados carimbados por nivel.
4. **Motor** (`motor-calculo`) — Wilson + pesos -> percentual + faixa + confianca.
5. **Parecer** (`parecer-jurimetrico`) — padrao combativo, com os motivos do numero.
6. **Auditoria** (`auditoria-jurimetrica`) — R1-R4. Sem aprovacao, retem.
7. **Dashboard** (`dashboard-jurimetrico`) — HTML standalone + PDF.

Argumento: `/jurimetria <descricao da demanda ou numero do processo>`.

Primeira vez? Rode **`/start-jurimetria`** para configurar e testar a chave do DataJud.

> Estimativa probabilistica com base em dados publicos e jurisprudencia. Nao constitui garantia de resultado.
