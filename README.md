# jurimetria-os-marketplace

> ## ⚖️ Este repositório NÃO é software livre
>
> O código fica visível para viabilizar a instalação no Claude/Cowork — não porque seja gratuito.
>
> **JURIMETRIA OS — R$ 298,00, pagamento único** (sem assinatura, sem recorrência)
> 👉 **[Adquirir a licença](https://pay.kirvano.com/47193fee-1fb3-4618-945d-c18694a7a196)**
>
> **Ao forkar ou clonar este repositório você adere à [licença de uso](LICENSE)**, devendo efetuar o
> pagamento no link acima e enviar o comprovante para **luis@sbroggio.com.br**.
>
> Os forks são públicos no GitHub e são registrados pelo titular (data, conta e repositório).
>
> **Já comprou?** Nada a fazer — sua licença cobre o uso e o fork para instalação. Este aviso vale de
> 11/08/2026 em diante, para quem chega ao repositório sem ter adquirido.


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
