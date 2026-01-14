# catches/management/commands/update_species_wiki.py
from __future__ import annotations

from django.core.management.base import BaseCommand
from catches.models import Species
from catches.services.wikipedia import fetch_wikipedia_summary_pt, try_extract_scientific_name_from_summary


class Command(BaseCommand):
    help = "Atualiza espécies com dados da Wikipedia (summary + image_url)."

    def add_arguments(self, parser):
        parser.add_argument("--slug", type=str, help="Atualiza apenas uma espécie pelo slug.")
        parser.add_argument("--force", action="store_true", help="Sobrescreve summary/image_url mesmo se já existir.")

    def handle(self, *args, **options):
        slug = options.get("slug")
        force = options.get("force", False)

        qs = Species.objects.all().order_by("name")
        if slug:
            qs = qs.filter(slug=slug)

        total = qs.count()
        ok = 0
        fail = 0
        skip = 0

        for s in qs:
            if not s.wikipedia_title:
                skip += 1
                continue

            data = fetch_wikipedia_summary_pt(s.wikipedia_title)
            if not data:
                fail += 1
                continue

            changed = False

            summary = data.get("summary")
            image_url = data.get("image_url")

            if force:
                if summary:
                    s.summary = summary
                    changed = True
                if image_url:
                    s.image_url = image_url
                    changed = True
            else:
                if summary and not s.summary:
                    s.summary = summary
                    changed = True
                if image_url and not s.image_url:
                    s.image_url = image_url
                    changed = True

            if not s.scientific_name and summary:
                sci = try_extract_scientific_name_from_summary(summary)
                if sci:
                    s.scientific_name = sci
                    changed = True

            if changed:
                s.save()
                ok += 1
            else:
                # já tinha tudo preenchido
                skip += 1

        self.stdout.write(self.style.SUCCESS(f"Total: {total} | OK: {ok} | Falhas: {fail} | Skips: {skip}"))
