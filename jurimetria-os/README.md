# jurimetria-os

**Motor de jurimetria preditiva para advogados.** A partir da descrição de uma demanda, cruza os dados empíricos do **DataJud (API pública do CNJ)** com a **jurisprudência** e entrega:

1. **Percentual de êxito** (procedência / improcedência / parcial) — sempre com **tamanho de amostra** e **intervalo de confiança** declarados.
2. **Parecer técnico** fundamentado (padrão combativo: FATO → NEXO → DIREITO).
3. **Dashboard visual** — HTML standalone + PDF executivo para anexar ao parecer.

## O que torna sério (não charlatão)
- **Anti-halucinação por design:** o número NUNCA sai sem `n` e intervalo de confiança. Amostra rasa → faixa larga + confiança BAIXA explícita, jamais um número falso-preciso.
- **Motor determinístico:** o cálculo (cliente DataJud + parser de movimentos TPU + intervalo de Wilson) é Python, não "achismo" do modelo. A IA orquestra e interpreta; o código conta e calcula.
- **Zero jurisprudência inventada:** cada citação é carimbada (validada / [VALIDAR] / impossibilidade); número, relator e ementa só entram se confirmados por fetch real.
- **Transparência de origem:** o parecer declara quanto do número veio do empírico, da jurisprudência e do ajuste fático.

## Comandos
- `/start-jurimetria` — configuração (testa a chave do DataJud).
- `/jurimetria <demanda>` — pipeline completo (triagem → coleta → cálculo → parecer → auditoria → dashboard).

## Requisitos
- **DataJud:** chave pública do CNJ (já embutida; renovável via env `DATAJUD_API_KEY`). Ver `CONNECTORS.md`.
- **Jurisprudência:** usa WebSearch/WebFetch nativos; Firecrawl/Bright Data/Tavily/Midpage são opcionais.

## Aviso
Estimativa probabilística com base em dados públicos e jurisprudência. **Não constitui garantia de resultado.** Ferramenta de apoio ao advogado habilitado.

---
IA Combativa — Família Adv-OS.
