# catches/admin.py
from __future__ import annotations

from decimal import Decimal
from django.contrib import admin, messages
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import redirect, get_object_or_404

from .models import Catch, Species, SpeciesPhoto, SpeciesBaitIdea
from .services.wikipedia import (
    fetch_wikipedia_summary_pt,
    try_extract_scientific_name_from_summary,
)


class SpeciesPhotoInline(admin.TabularInline):
    model = SpeciesPhoto
    extra = 1
    fields = ("image", "caption", "created_at")
    readonly_fields = ("created_at",)


class SpeciesBaitIdeaInline(admin.TabularInline):
    model = SpeciesBaitIdea
    extra = 1
    fields = ("bait_name", "notes")


def fmt_decimal_br(value: Decimal | None) -> str:
    """
    Mostra Decimal sem zeros finais.
    Ex:
      30.00 -> "30"
      30.50 -> "30,5"
      30.25 -> "30,25"
    """
    if value is None:
        return "-"
    if value == value.to_integral():
        return str(int(value))
    s = format(value.normalize(), "f").rstrip("0").rstrip(".")
    return s.replace(".", ",")


@admin.register(Species)
class SpeciesAdmin(admin.ModelAdmin):
    inlines = [SpeciesPhotoInline, SpeciesBaitIdeaInline]

    list_display = (
        "cover_thumb",
        "name",
        "min_length_fmt",
        "points_per_cm_fmt",
        "is_competition_allowed",
        "wiki_status",
        "wiki_update_btn",
        "updated_at",
    )
    list_filter = ("is_competition_allowed",)
    search_fields = ("name", "scientific_name", "slug", "wikipedia_title")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)

    actions = ["fetch_from_wikipedia_action"]

    @admin.display(description="Foto")
    def cover_thumb(self, obj: Species):
        url = getattr(obj, "cover_image", None)
        # cover_image é @property no seu model, retorna url ou None
        if callable(url):
            url = url()
        if not url:
            return format_html("<span style='color:#999'>—</span>")
        return format_html(
            "<img src='{}' style='height:38px;width:60px;object-fit:cover;border-radius:8px;border:1px solid #333;'/>",
            url
        )

    @admin.display(description="Comprimento mínimo (cm)", ordering="min_length_cm")
    def min_length_fmt(self, obj: Species):
        return fmt_decimal_br(obj.min_length_cm)

    @admin.display(description="Pontos por centímetro", ordering="points_per_cm")
    def points_per_cm_fmt(self, obj: Species):
        return fmt_decimal_br(obj.points_per_cm)

    @admin.display(description="Wiki")
    def wiki_status(self, obj: Species):
        has_title = bool(obj.wikipedia_title)
        has_summary = bool(obj.summary)
        has_image = bool(obj.image_url)

        if not has_title:
            return "—"

        ok = (has_summary or has_image)
        return "✅ OK" if ok else "⚠️ vazio"

    @admin.display(description="Atualizar")
    def wiki_update_btn(self, obj: Species):
        if not obj.wikipedia_title:
            return format_html("<span style='color:#999'>Sem título</span>")
        return format_html(
            "<a class='button' href='{}'>Atualizar Wiki</a>",
            f"wiki-update/{obj.pk}/"
        )

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "wiki-update/<int:pk>/",
                self.admin_site.admin_view(self.wiki_update_view),
                name="species_wiki_update",
            ),
        ]
        return custom + urls

    def wiki_update_view(self, request, pk: int):
        species = get_object_or_404(Species, pk=pk)
        updated = self._enrich_species_from_wiki(species)

        if updated:
            self.message_user(
                request,
                f"Espécie '{species.name}' atualizada via Wikipedia.",
                level=messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                f"Não foi possível atualizar '{species.name}'. Verifique o Título na Wikipedia ou conectividade.",
                level=messages.WARNING
            )
        return redirect("..")

    @admin.action(description="Buscar dados da Wikipedia (selecionadas)")
    def fetch_from_wikipedia_action(self, request, queryset):
        ok = 0
        skip = 0

        for species in queryset:
            if not species.wikipedia_title:
                skip += 1
                continue
            if self._enrich_species_from_wiki(species):
                ok += 1

        if ok:
            self.message_user(request, f"{ok} espécie(s) atualizada(s) via Wikipedia.", level=messages.SUCCESS)
        if skip:
            self.message_user(request, f"{skip} sem wikipedia_title (puladas).", level=messages.INFO)

    def _enrich_species_from_wiki(self, species: Species) -> bool:
        """
        Atualiza species.summary e species.image_url (e tenta scientific_name) com base no wikipedia_title.
        Retorna True se atualizou algo.
        """
        if not species.wikipedia_title:
            return False

        data = fetch_wikipedia_summary_pt(species.wikipedia_title)
        if not data:
            return False

        changed = False

        summary = data.get("summary")
        if summary and (not species.summary or species.summary.strip() == ""):
            species.summary = summary
            changed = True

        image_url = data.get("image_url")
        if image_url and (not species.image_url or species.image_url.strip() == ""):
            species.image_url = image_url
            changed = True

        if not species.scientific_name and summary:
            sci = try_extract_scientific_name_from_summary(summary)
            if sci:
                species.scientific_name = sci
                changed = True

        if changed:
            species.save()

        return changed


@admin.register(Catch)
class CatchAdmin(admin.ModelAdmin):
    list_display = (
        "member",
        "species",
        "length_cm",
        "weight_kg",
        "caught_at",
        "bait",
        "location",
        "points_display",
    )
    list_select_related = ("member", "species")
    search_fields = ("member__name", "species__name", "location", "bait")

    @admin.display(description="Pontos")
    def points_display(self, obj: Catch):
        pts = obj.calc_points()
        if pts is None:
            return "-"
        return f"{int(pts)}"
