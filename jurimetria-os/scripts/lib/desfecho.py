"""desfecho.py — parser de movimentos DataJud -> desfecho do processo.

Regra de ouro (anti-halucinacao): decidir SEMPRE por codigo inteiro, NUNCA por
texto (nomes da TPU tem placeholders e acentuacao variavel entre tribunais).
Mais recente vence. Recursal e separado de 1o grau. Se nada bate -> INDEFINIDO.
"""

from __future__ import annotations
from . import tpu


def _data_mov(m: dict) -> str:
    return m.get("dataHora", "") or ""


def classificar_processo(source: dict) -> dict:
    """Recebe um _source do DataJud e devolve o desfecho legivel (1o grau) + recursal.

    Retorna: {desfecho, desfecho_recursal, transitado, tem_movimentos}
    desfecho in {PROCEDENTE, IMPROCEDENTE, PARCIALMENTE_PROCEDENTE, ACORDO_HOMOLOGADO,
                 EXTINTO_SEM_MERITO, ... , INDEFINIDO}
    """
    movimentos = source.get("movimentos") or []
    if not movimentos:
        return {"desfecho": "INDEFINIDO", "desfecho_recursal": None,
                "transitado": False, "tem_movimentos": False}

    # Ordena por dataHora decrescente — o desfecho mais recente prevalece.
    movs = sorted(movimentos, key=_data_mov, reverse=True)

    desfecho = "INDEFINIDO"
    recursal = None
    transitado = False

    for m in movs:
        cod = m.get("codigo")
        try:
            cod = int(cod)
        except (TypeError, ValueError):
            continue

        if cod == tpu.MOVIMENTO_TRANSITO_JULGADO:
            transitado = True

        if recursal is None and cod in tpu.DESFECHO_RECURSAL:
            recursal = tpu.DESFECHO_RECURSAL[cod]

        if desfecho == "INDEFINIDO":
            if cod in tpu.DESFECHO_POR_MOVIMENTO:
                desfecho = tpu.DESFECHO_POR_MOVIMENTO[cod]
            elif cod in tpu.MOVIMENTOS_COM_COMPLEMENTO_RESULTADO:
                for comp in (m.get("complementosTabelados") or []):
                    cc = comp.get("codigo")
                    try:
                        cc = int(cc)
                    except (TypeError, ValueError):
                        continue
                    if cc in tpu.RESULTADO_POR_COMPLEMENTO:
                        desfecho = tpu.RESULTADO_POR_COMPLEMENTO[cc]
                        break

    return {"desfecho": desfecho, "desfecho_recursal": recursal,
            "transitado": transitado, "tem_movimentos": True}


def agregar(processos_source: list[dict], polo_cliente: str = "ativo") -> dict:
    """Agrega desfechos de uma lista de _source. polo_cliente: 'ativo' (autor) ou 'passivo' (reu).

    Conta apenas processos com desfecho LEGIVEL de 1o grau. Os demais entram em
    n_total mas nao em n_com_desfecho — transparencia (R-JURI-01).
    """
    n_total = len(processos_source)
    contagem: dict[str, int] = {}
    n_com_desfecho = 0

    for src in processos_source:
        d = classificar_processo(src)["desfecho"]
        if d == "INDEFINIDO":
            continue
        n_com_desfecho += 1
        contagem[d] = contagem.get(d, 0) + 1

    proc = contagem.get("PROCEDENTE", 0)
    imp = contagem.get("IMPROCEDENTE", 0)
    parc = contagem.get("PARCIALMENTE_PROCEDENTE", 0)
    acordo = contagem.get("ACORDO_HOMOLOGADO", 0)

    # "Exito" depende do polo do cliente. Procedencia favorece o autor; desfavorece o reu.
    if polo_cliente == "passivo":
        exito = imp + parc * 0.5  # parcial e exito parcial p/ ambos
    else:
        exito = proc + parc * 0.5

    base = n_com_desfecho if n_com_desfecho else 1
    return {
        "n_total": n_total,
        "n_com_desfecho": n_com_desfecho,
        "contagem": contagem,
        "taxa_procedencia": round(proc / base, 4) if n_com_desfecho else None,
        "taxa_improcedencia": round(imp / base, 4) if n_com_desfecho else None,
        "taxa_parcial": round(parc / base, 4) if n_com_desfecho else None,
        "taxa_acordo": round(acordo / base, 4) if n_com_desfecho else None,
        "sucessos_polo": round(exito, 2),
        "taxa_exito_polo": round(exito / base, 4) if n_com_desfecho else None,
        "polo_cliente": polo_cliente,
    }
