# jurimetria-os-marketplace

Marketplace oficial do plugin **Jurimetria OS** (família IA Combativa).

**Motor de jurimetria preditiva para advogados.** A partir da descrição de uma demanda, cruza os dados empíricos do **DataJud (API pública do CNJ)** com a **jurisprudência** e entrega: percentual de êxito (com amostra + intervalo de confiança), parecer técnico fundamentado e dashboard visual (HTML + PDF).

## Diferencial — sério, não charlatão
- **Anti-halucinação por design:** número nunca sai sem `n` e intervalo de confiança; amostra rasa → confiança BAIXA explícita.
- **Motor determinístico:** cálculo em Python (DataJud + parser TPU + intervalo de Wilson), não "achismo" do modelo.
- **Zero jurisprudência inventada:** cada citação carimbada; nº/relator/ementa só com fetch real.

## Instalação (Claude Cowork)
1. Cowork → **Settings → Plugins** → aba **Pessoal** → **"+"** → **Adicionar marketplace**.
2. Cole a URL deste repositório → **Sincronizar**.
3. Instale **jurimetria-os** e rode **`/start-jurimetria`** (testa a chave do DataJud).

## Comandos
- `/start-jurimetria` — configuração.
- `/jurimetria <demanda>` — pipeline completo.

## Aviso
Estimativa probabilística com base em dados públicos e jurisprudência. **Não constitui garantia de resultado.**

---
IA Combativa — Família Adv-OS.
