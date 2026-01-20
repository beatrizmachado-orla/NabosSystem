# catches/views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import DetailView, CreateView, ListView
from django.shortcuts import redirect
from django.db.models import Count
from .models import Catch, Species
from .forms import CatchCreateForm

# opcional
from .services.wikipedia import fetch_wikipedia_summary_pt, try_extract_scientific_name_from_summary


class CatchCreateView(LoginRequiredMixin, CreateView):
    model = Catch
    form_class = CatchCreateForm
    template_name = "catches/catch_form.html"
    success_url = reverse_lazy("my_profile")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not hasattr(request.user, "member"):
            return redirect("my_profile")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.member = self.request.user.member
        return super().form_valid(form)


class SpeciesDetailView(DetailView):
    model = Species
    template_name = "catches/species_detail.html"
    context_object_name = "species"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return (
            Species.objects
            .prefetch_related("photos", "bait_ideas")
            .annotate(catches_count=Count("catches"))
        )

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)

        # ✅ OPCIONAL: auto-enrich se estiver vazio
        if obj.wikipedia_title and (not obj.summary or not obj.image_url):
            data = fetch_wikipedia_summary_pt(obj.wikipedia_title)
            if data:
                changed = False
                if (not obj.summary) and data.get("summary"):
                    obj.summary = data["summary"]
                    changed = True
                if (not obj.image_url) and data.get("image_url"):
                    obj.image_url = data["image_url"]
                    changed = True
                if not obj.scientific_name and obj.summary:
                    sci = try_extract_scientific_name_from_summary(obj.summary)
                    if sci:
                        obj.scientific_name = sci
                        changed = True
                if changed:
                    obj.save()

        return obj

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        s = self.object

        recent = (
            s.catches.select_related("member")
            .order_by("-caught_at")[:12]
        )
        ctx["recent_catches"] = recent
        return ctx


class CatchDetailView(LoginRequiredMixin, DetailView):
    model = Catch
    template_name = "catches/catch_detail.html"
    context_object_name = "catch"

    def get_queryset(self):
        qs = super().get_queryset().select_related("member", "species")
        return qs

class CompetitionSpeciesListView(ListView):
    model = Species
    template_name = "catches/species_competition_list.html"
    context_object_name = "species_list"
    paginate_by = 24

    def get_queryset(self):
        q = (self.request.GET.get("q") or "").strip()
        qs = (
            Species.objects
            .filter(is_competition_allowed=True)
            .annotate(catches_count=Count("catches"))
            .prefetch_related("photos")
            .order_by("name")
        )
        if q:
            qs = qs.filter(name__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = (self.request.GET.get("q") or "").strip()
        return ctx