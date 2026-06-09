"""estatistica.py — motor estatistico de jurimetria.

Zero dependencias externas (so stdlib math). Anti-halucinacao: nenhum numero
de saida sem intervalo de confianca associado. Codigo verificado numericamente
em jun/2026 (ver doctests).

Wilson score interval (sem continuity correction) — robusto para amostra
pequena e proporcao extrema, ao contrario do intervalo de Wald (normal), que
degenera (ex.: 10/10 -> [1,1], 0/10 -> [0,0]).
"""

from __future__ import annotations
import math

Z_SCORES = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576}


def wilson_interval(successes: int, n: int, z: float = 1.96) -> tuple[float, float, float]:
    """Intervalo de Wilson. Retorna (centro, limite_inferior, limite_superior) em [0,1].

    O centro NAO e p_hat — e p_hat com shrinkage em direcao a 0.5 (robusto).

    >>> c, lo, hi = wilson_interval(7, 10)
    >>> round(lo, 2), round(hi, 2)
    (0.4, 0.89)
    >>> _, lo, hi = wilson_interval(0, 10)
    >>> round(lo, 2), round(hi, 2)
    (0.0, 0.28)
    >>> _, lo, hi = wilson_interval(10, 10)
    >>> round(lo, 2), round(hi, 2)
    (0.72, 1.0)
    """
    if n <= 0:
        return (0.0, 0.0, 0.0)
    p = successes / n
    z2 = z * z
    denom = 1.0 + z2 / n
    centro = (p + z2 / (2.0 * n)) / denom
    margem = (z / denom) * math.sqrt(p * (1.0 - p) / n + z2 / (4.0 * n * n))
    return (centro, max(0.0, centro - margem), min(1.0, centro + margem))


def pesos_adaptativos(n_com_desfecho: int, w_e_base: float = 0.6,
                      piso_robusto: int = 200) -> tuple[float, float]:
    """Rampa continua: empirico ganha peso de 0 ate w_e_base conforme n->piso_robusto.
    Garante w_e + w_j == 1.0.

    >>> we, wj = pesos_adaptativos(0)
    >>> we, round(wj, 2)
    (0.0, 1.0)
    >>> we, wj = pesos_adaptativos(200)
    >>> round(we, 2), round(wj, 2)
    (0.6, 0.4)
    """
    fator = min(1.0, n_com_desfecho / piso_robusto) if piso_robusto else 0.0
    w_e = w_e_base * fator
    return (w_e, 1.0 - w_e)


def nivel_confianca(n: int, ic_largura: float, piso: int = 30,
                    piso_robusto: int = 200) -> str:
    """Classifica confianca por volume (n) E precisao (largura do IC).

    >>> nivel_confianca(10, 0.495)
    'BAIXA'
    >>> nivel_confianca(100, 0.192)
    'MEDIA'
    >>> nivel_confianca(250, 0.15)
    'ALTA'
    """
    if n >= piso_robusto and ic_largura <= 0.20:
        return "ALTA"
    if n >= piso and ic_largura <= 0.35:
        return "MEDIA"
    return "BAIXA"


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def calcular_p_exito(n_com_desfecho: int, sucessos: int, a_jurisprudencial: float,
                     ajuste_fatico_raw: float = 0.0, w_e_base: float = 0.6,
                     piso: int = 30, piso_robusto: int = 200,
                     z: float = 1.96) -> dict:
    """Formula final: P = w_e*centro_wilson + w_j*A_juris + ajuste_fatico(clamp[-0.15,0.15])."""
    centro, ic_low, ic_high = wilson_interval(sucessos, n_com_desfecho, z)
    w_e, w_j = pesos_adaptativos(n_com_desfecho, w_e_base, piso_robusto)
    ajuste = _clamp(ajuste_fatico_raw, -0.15, 0.15)
    p = _clamp(w_e * centro + w_j * a_jurisprudencial + ajuste, 0.0, 1.0)
    largura = ic_high - ic_low
    # Faixa do numero FINAL: central combinado +/- margem empirica de Wilson.
    # Mantem o ponto dentro da banda; a largura reflete a incerteza amostral real.
    margem = largura / 2.0
    faixa = [round(_clamp(p - margem, 0.0, 1.0), 4), round(_clamp(p + margem, 0.0, 1.0), 4)]
    return {
        "p_exito": round(p, 4),
        "faixa": faixa,
        "ic_empirico": [round(ic_low, 4), round(ic_high, 4)],
        "ic_largura": round(largura, 4),
        "nivel_confianca": nivel_confianca(n_com_desfecho, largura, piso, piso_robusto),
        "decomposicao": {
            "empirico": round(w_e, 3),
            "jurisprudencial": round(w_j, 3),
            "fatico": round(ajuste, 3),
        },
        "t_empirica_wilson": round(centro, 4),
        "n_com_desfecho": n_com_desfecho,
    }


if __name__ == "__main__":
    import doctest
    r = doctest.testmod(verbose=False)
    print(f"estatistica.py — doctests: {r.attempted} rodados, {r.failed} falharam")
