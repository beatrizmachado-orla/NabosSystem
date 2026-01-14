# catches/services/wikipedia.py
from __future__ import annotations

import re
import requests
from typing import Optional, Dict, Any

WIKI_SUMMARY_PT = "https://pt.wikipedia.org/api/rest_v1/page/summary/"


def _clean_title(title: str) -> str:
    title = (title or "").strip()
    title = title.replace(" ", "_")
    return title


def fetch_wikipedia_summary_pt(title: str, timeout: int = 10) -> Optional[Dict[str, Any]]:
    """
    Busca dados básicos da Wikipedia PT via REST summary:
    - title
    - extract (summary)
    - thumbnail.source (image_url)
    - content_urls.desktop.page (url)
    """
    if not title:
        return None

    safe_title = _clean_title(title)
    url = f"{WIKI_SUMMARY_PT}{safe_title}"

    try:
        r = requests.get(
            url,
            timeout=timeout,
            headers={"User-Agent": "NabosSystem/1.0 (Species Enrichment)"},
        )
        if r.status_code != 200:
            return None

        data = r.json() or {}
        return {
            "title": data.get("title"),
            "summary": data.get("extract"),
            "image_url": (data.get("thumbnail") or {}).get("source"),
            "page_url": ((data.get("content_urls") or {}).get("desktop") or {}).get("page"),
        }
    except requests.RequestException:
        return None


def try_extract_scientific_name_from_summary(summary: str) -> Optional[str]:
    """
    Heurística simples (opcional) pra tentar puxar nome científico do resumo:
    - procura por padrão "Nome (Genus species)" ou "(Genus species)"
    Não é perfeito, mas ajuda.
    """
    if not summary:
        return None

    # tenta encontrar algo como (Genus species) com inicial maiúscula e segunda palavra minúscula
    m = re.search(r"\(([A-Z][a-z]+(?:\s[a-z]+){1,2})\)", summary)
    if not m:
        return None

    sci = m.group(1).strip()
    # evita pegar coisas tipo (Portugal) etc
    if " " not in sci:
        return None
    return sci
