# catches/management/commands/fill_wikipedia_titles.py
from __future__ import annotations

import re
import requests
from django.core.management.base import BaseCommand
from catches.models import Species

UA = "NabosSystem/1.0 (contact: dev@nabos.local)"


def normalize_title(s: str) -> str:
    s = (s or "").strip()
    s = re.sub(r"\s+", " ", s)
    return s


def wiki_opensearch_pt(query: str) -> str | None:
    """
    Retorna o melhor título sugerido pela Wikipedia PT para uma busca.
    Usa opensearch (rápido).
    """
    if not query:
        return None

    url = "https://pt.wikipedia.org/w/api.php"
    params = {
        "action": "opensearch",
        "format": "json",
        "search": query,
        "limit": 1,
        "namespace": 0,
        "redirects": "resolve",
    }
    r = requests.get(url, params=params, timeout=10, headers={"User-Agent": UA})
    if r.status_code != 200:
        return None

    data = r.json()
    # formato: [search, [titles], [descriptions], [urls]]
    titles = data[1] if len(data) > 1 else []
    if titles:
        return normalize_title(titles[0])
    return None


def page_exists_pt(title: str) -> bool:
    """
    Confere se a página existe na Wikipedia PT.
    """
    if not title:
        return False

    url = "https://pt.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "titles": title,
    }
    r = requests.get(url, params=params, timeout=10, headers={"User-Agent": UA})
    if r.status_code != 200:
        return False
    data = r.json()
    pages = (data.get("query") or {}).get("pages") or {}
    for _, page in pages.items():
        # pageid = -1 indica inexistente
        if page.get("missing") is not None:
            return False
    return True


class Command(BaseCommand):
    help = "Preenche Species.wikipedia_title automaticamente a partir do nome (Wikipedia PT)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Sobrescreve wikipedia_title mesmo se já estiver preenchido.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="Limita a quantidade de espécies processadas (0 = todas).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Mostra o que faria, mas não salva.",
        )

    def handle(self, *args, **opts):
        force: bool = opts["force"]
        limit: int = opts["limit"]
        dry: bool = opts["dry_run"]

        qs = Species.objects.all().order_by("name")
        if not force:
            qs = qs.filter(wikipedia_title__isnull=True) | qs.filter(wikipedia_title__exact="")
            qs = qs.order_by("name")

        if limit and limit > 0:
            qs = qs[:limit]

        total = qs.count()
        ok = fail = skip = 0

        for s in qs:
            if (s.wikipedia_title and not force):
                skip += 1
                continue

            query = s.name
            try:
                guess = wiki_opensearch_pt(query)

                if not guess:
                    skip += 1
                    self.stdout.write(f"[SKIP] {s.name} -> sem sugestão")
                    continue

                # valida que existe
                if not page_exists_pt(guess):
                    skip += 1
                    self.stdout.write(f"[SKIP] {s.name} -> sugestão '{guess}' não existe")
                    continue

                if dry:
                    self.stdout.write(f"[DRY] {s.name} -> wikipedia_title='{guess}'")
                else:
                    s.wikipedia_title = guess
                    s.save(update_fields=["wikipedia_title"])
                    self.stdout.write(self.style.SUCCESS(f"[OK] {s.name} -> {guess}"))
                ok += 1

            except Exception as e:
                fail += 1
                self.stdout.write(self.style.ERROR(f"[FAIL] {s.name}: {e}"))

        self.stdout.write(self.style.SUCCESS(f"Total: {total} | OK: {ok} | Falhas: {fail} | Skips: {skip}"))
