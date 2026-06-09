"""datajud_client.py — cliente da API publica do DataJud (CNJ), via Elasticsearch.

Verificado ao vivo (curl HTTP 200) em jun/2026. So stdlib (urllib) — zero deps.

PEGADINHAS TRATADAS (todas observadas na API real):
- Chave publica rotaciona; o portal antigo do CNJ publica uma chave MORTA (401).
  Fonte de verdade: https://datajud-wiki.cnj.jus.br/api-publica/acesso/
  Sempre smoke_test() antes de confiar.
- dataAjuizamento tem 2 formatos no mesmo campo (ISO e cru yyyyMMddHHmmss); o
  filtro range so casa com ISO. Filtrar em cru retorna 0 hits SEM erro.
- movimentos pode estar ausente -> source.get("movimentos", []).
- janela de 10.000 (from+size); acima exige search_after.
- @timestamp nao e unico -> tie-breaker com _id no sort.
- track_total_hits:true para contagem exata (sem isso satura em 10000).
"""

from __future__ import annotations
import json
import os
import urllib.request
import urllib.error

# Chave PUBLICA do DataJud (publicada pelo CNJ). Verificada HTTP 200 em 2026-06-09.
# Pode rotacionar — renovar em https://datajud-wiki.cnj.jus.br/api-publica/acesso/
DEFAULT_PUBLIC_KEY = "cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw=="
WIKI_ACESSO = "https://datajud-wiki.cnj.jus.br/api-publica/acesso/"
BASE = "https://api-publica.datajud.cnj.jus.br/api_publica_{alias}/_search"


def get_api_key() -> str:
    return os.environ.get("DATAJUD_API_KEY", DEFAULT_PUBLIC_KEY)


def _post(alias: str, body: dict, timeout: int = 30) -> dict:
    url = BASE.format(alias=alias)
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"APIKey {get_api_key()}")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:300]
        raise RuntimeError(f"DataJud HTTP {e.code} ({alias}): {detail}") from e


def smoke_test(alias: str = "tjsp") -> tuple[bool, str]:
    """Valida a chave/endpoint com um match_all size:0. Retorna (ok, mensagem)."""
    try:
        r = _post(alias, {"size": 0, "query": {"match_all": {}}})
        total = r.get("hits", {}).get("total", {}).get("value")
        return True, f"OK — {alias} respondeu (total>={total})"
    except RuntimeError as e:
        msg = str(e)
        if "401" in msg:
            return False, f"CHAVE INVALIDA/ROTACIONADA (401). Renove em {WIKI_ACESSO}"
        return False, msg


def montar_query(*, classe: int | None = None, assuntos: list[int] | None = None,
                 orgao: int | None = None, data_inicio: str | None = None,
                 data_fim: str | None = None, grau: str | None = None,
                 size: int = 100) -> dict:
    """Monta o body Elasticsearch (bool term + range ISO). Datas em 'yyyy-MM-dd'."""
    must: list[dict] = []
    filt: list[dict] = []
    if classe is not None:
        must.append({"term": {"classe.codigo": classe}})
    if assuntos:
        for a in assuntos:
            must.append({"term": {"assuntos.codigo": a}})
    if orgao is not None:
        filt.append({"term": {"orgaoJulgador.codigo": orgao}})
    if grau:
        filt.append({"term": {"grau": grau}})
    if data_inicio or data_fim:
        rng: dict = {}
        if data_inicio:
            rng["gte"] = data_inicio  # ISO yyyy-MM-dd — NUNCA yyyyMMdd
        if data_fim:
            rng["lte"] = data_fim
        filt.append({"range": {"dataAjuizamento": rng}})
    if not must:
        must.append({"match_all": {}})
    return {
        "size": size,
        "track_total_hits": True,
        "query": {"bool": {"must": must, "filter": filt}},
        # Ordenacao por @timestamp (padrao oficial CNJ). NAO usar _id como
        # tie-breaker: o cluster do DataJud proibe fielddata em _id (HTTP 400).
        "sort": [{"@timestamp": {"order": "asc"}}],
    }


def coletar(alias: str, query_body: dict, max_processos: int = 2000,
            page_size: int = 100) -> dict:
    """Pagina via search_after ate esgotar ou atingir max_processos.

    Retorna {total_declarado, sources:[_source...], paginas}.
    """
    body = dict(query_body)
    body["size"] = page_size
    sources: list[dict] = []
    search_after = None
    paginas = 0
    total_declarado = None

    while len(sources) < max_processos:
        b = dict(body)
        if search_after is not None:
            b["search_after"] = search_after
        r = _post(alias, b)
        paginas += 1
        if total_declarado is None:
            total_declarado = r.get("hits", {}).get("total", {}).get("value")
        hits = r.get("hits", {}).get("hits", [])
        if not hits:
            break
        for h in hits:
            sources.append(h.get("_source", {}))
        search_after = hits[-1].get("sort")
        if search_after is None or len(hits) < page_size:
            break

    return {"total_declarado": total_declarado, "sources": sources, "paginas": paginas}


def normalizar_data(v: str | None) -> str | None:
    """Normaliza dataAjuizamento (ISO ou cru yyyyMMddHHmmss) -> ISO yyyy-MM-dd."""
    if not v:
        return None
    v = str(v)
    if "T" in v or "-" in v:
        return v[:10]
    if len(v) >= 8 and v.isdigit():
        return f"{v[0:4]}-{v[4:6]}-{v[6:8]}"
    return v
