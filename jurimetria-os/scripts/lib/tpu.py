"""tpu.py — Tabelas Processuais Unificadas (TPU/CNJ) relevantes para jurimetria.

Fonte de verdade: SGT/CNJ (consulta publica de movimentos/classes, tabela
v26/05/2026) + planilhas oficiais CNJ/TST. Verificado em jun/2026.

PRINCIPIO: o desfecho de um processo e o CODIGO DO MOVIMENTO, nao um
complemento. O PRD original errou (afirmava complemento 3/4/5). Os codigos
reais estao abaixo. NUNCA decidir desfecho por texto/nome — so por codigo.
"""

from __future__ import annotations

# Movimento -> desfecho de 1o grau (com resolucao de merito, pai 385).
# Verificado contra a TPU oficial de Movimentos (CNJ/TST).
DESFECHO_POR_MOVIMENTO: dict[int, str] = {
    # --- Com resolucao do merito (pai 385) ---
    219: "PROCEDENTE",                 # Julgado(s) procedente(s) o(s) pedido(s)
    220: "IMPROCEDENTE",               # Julgado(s) improcedente(s) o(s) pedido(s)
    221: "PARCIALMENTE_PROCEDENTE",    # Julgado(s) procedente(s) em parte
    50103: "IMPROCEDENTE",            # Liminarmente improcedente (art. 332 CPC)
    471: "EXTINTO_MERITO",            # Decadencia/prescricao (art. 487, II)
    # 50094 (julgamento antecipado parcial) -> decidir pelo complemento (ver abaixo)
    # --- Autocomposicao (merito, art. 487, III) ---
    466: "ACORDO_HOMOLOGADO",         # Homologada a transacao
    11795: "RECONHECIMENTO_PROCEDENCIA",
    455: "RENUNCIA_HOMOLOGADA",
    377: "ACORDO_HOMOLOGADO",         # acordo em execucao/cumprimento
    14099: "ACORDO_HOMOLOGADO",
    # --- Sem resolucao do merito (pai 218/456) ---
    454: "EXTINTO_SEM_MERITO",        # indeferimento da inicial
    459: "EXTINTO_SEM_MERITO",        # ausencia de pressupostos
    460: "EXTINTO_SEM_MERITO",        # perempcao/litispendencia/coisa julgada
    461: "EXTINTO_SEM_MERITO",        # ausencia de legitimidade/interesse
    457: "EXTINTO_SEM_MERITO",        # negligencia
    458: "EXTINTO_SEM_MERITO",        # abandono
    463: "DESISTENCIA_HOMOLOGADA",
    # --- Execucao ---
    196: "EXECUCAO_EXTINTA",
}

# Movimentos genericos cujo desfecho vem do complemento "Resultado do julgamento".
MOVIMENTOS_COM_COMPLEMENTO_RESULTADO: set[int] = {50094}

# Complemento "Resultado do julgamento" -> desfecho. codigo do VALOR do complemento.
RESULTADO_POR_COMPLEMENTO: dict[int, str] = {
    7462: "PROCEDENTE",
    7463: "IMPROCEDENTE",
    7464: "PARCIALMENTE_PROCEDENTE",
}

# Movimentos RECURSAIS (2o grau / turma) — instancia separada, NAO contar como 1o grau.
DESFECHO_RECURSAL: dict[int, str] = {
    237: "RECURSO_PROVIDO",
    238: "RECURSO_PARCIALMENTE_PROVIDO",
    239: "RECURSO_NAO_PROVIDO",
    235: "RECURSO_NAO_CONHECIDO",
    236: "RECURSO_NEGADO_SEGUIMENTO",
}

# Flag (nao e desfecho).
MOVIMENTO_TRANSITO_JULGADO = 848

# Quais desfechos contam como EXITO para o polo ATIVO (autor).
# Para o polo PASSIVO (reu), inverte-se PROCEDENTE<->IMPROCEDENTE (ver desfecho.py).
EXITO_AUTOR = {"PROCEDENTE", "PARCIALMENTE_PROCEDENTE", "RECONHECIMENTO_PROCEDENCIA"}
DERROTA_AUTOR = {"IMPROCEDENTE"}
NEUTRO = {"ACORDO_HOMOLOGADO", "RENUNCIA_HOMOLOGADA", "EXTINTO_SEM_MERITO",
          "DESISTENCIA_HOMOLOGADA", "EXTINTO_MERITO", "EXECUCAO_EXTINTA"}

# Classes TPU comuns (parametrizacao CNJ 2024). DE-PARA NL->codigo na triagem.
CLASSES_COMUNS: dict[int, str] = {
    7: "Procedimento Comum Civel",
    22: "Procedimento Sumario",
    40: "Monitoria",
    81: "Busca e Apreensao em Alienacao Fiduciaria",
    93: "Despejo por Falta de Pagamento",
    436: "Procedimento do Juizado Especial Civel",
    156: "Cumprimento de Sentenca",
    157: "Cumprimento Provisorio de Sentenca",
    159: "Execucao de Titulo Extrajudicial",
    1116: "Execucao Fiscal",
    1118: "Embargos a Execucao Fiscal",
}
# Variantes de "Execucao de Titulo Extrajudicial" (revisoes da TPU). Aceitar o conjunto.
CLASSES_EXEC_TITULO_EXTRAJUDICIAL = {159, 990, 12154}

# Assuntos: ~13 mil entradas. NAO hardcodar — consultar SGT em runtime / triagem.
SGT_CONSULTA_ASSUNTOS = "https://www.cnj.jus.br/sgt/consulta_publica_assuntos.php"
SGT_CONSULTA_CLASSES = "https://www.cnj.jus.br/sgt/consulta_publica_classes.php"
SGT_CONSULTA_MOVIMENTOS = "https://www.cnj.jus.br/sgt/consulta_publica_movimentos.php"

# Metadados de proveniencia (anti-halucinacao: data + fonte sempre declaradas).
TPU_META = {
    "versao_tabela": "2026-05-26",
    "fonte": "SGT/CNJ + planilhas oficiais CNJ/TST",
    "extraido_em": "2026-06-09",
    "aviso": "Codigos podem mudar em novas versoes da TPU. Reconfirmar no SGT antes de release.",
}
