"""canonical.py — schema canonico de resultado da jurimetria (1 fonte da verdade).

Tudo (coleta_datajud, coleta_jurisprudencia, motor, dashboard) consome/produz
este mesmo formato. Mudou aqui, mudou em todo o pipeline.
"""

from __future__ import annotations

SCHEMA_VERSION = "1.0"

DISCLAIMER = (
    "Estimativa probabilistica com base em dados publicos (DataJud/CNJ) e "
    "jurisprudencia. NAO constitui garantia de resultado. O numero acompanha "
    "sempre o tamanho da amostra com desfecho legivel e o intervalo de confianca."
)


def resultado_canonico(*, triagem: dict, empirico: dict | None,
                       jurisprudencia: dict | None, motor: dict | None,
                       gerado_em: str) -> dict:
    """Monta o objeto canonico. Campos None quando a etapa nao rodou (degradacao)."""
    return {
        "schema_version": SCHEMA_VERSION,
        "gerado_em": gerado_em,
        "triagem": triagem,                 # materia, classe, assuntos, tribunal, polo, tese
        "empirico": empirico,               # saida de desfecho.agregar() + tempo_medio
        "jurisprudencia": jurisprudencia,   # {favoravel, desfavoravel, neutro, citacoes[]}
        "motor": motor,                     # saida de estatistica.calcular_p_exito()
        "fontes": {
            "datajud": bool(empirico),
            "jurisprudencia_validada": (jurisprudencia or {}).get("n_validada", 0),
            "jurisprudencia_indicativa": (jurisprudencia or {}).get("n_indicativa", 0),
        },
        "disclaimer": DISCLAIMER,
    }


def saida_motor(p_exito: dict, empirico: dict) -> dict:
    """Formato §6.4 do PRD a partir da saida do estatistica.calcular_p_exito."""
    return {
        "p_exito_central": p_exito.get("p_exito"),
        "faixa": p_exito.get("faixa", [0, 0]),
        "ic_empirico": p_exito.get("ic_empirico"),
        "intervalo_confianca": "95%",
        "nivel_confianca": p_exito.get("nivel_confianca"),
        "amostra": {
            "n_total": empirico.get("n_total"),
            "n_com_desfecho": empirico.get("n_com_desfecho"),
        },
        "decomposicao": p_exito.get("decomposicao"),
    }
