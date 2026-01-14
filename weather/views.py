# weather/views.py
from django.views.generic import ListView, DetailView
from django.utils import timezone
from django.db.models import Count
from datetime import timedelta
from .models import Spot, ForecastHour


class SpotsListView(ListView):
    model = Spot
    template_name = "weather/spots_list.html"
    context_object_name = "spots"

    def get_queryset(self):
        qs = Spot.objects.filter(is_active=True).order_by("name")
        q = (self.request.GET.get("q") or "").strip()
        if q:
            qs = qs.filter(name__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = (self.request.GET.get("q") or "").strip()
        return ctx


class SpotDetailView(DetailView):
    model = Spot
    template_name = "weather/spot_detail.html"
    context_object_name = "spot"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # todas as horas já salvas no banco
        hours = list(
            self.object.forecast_hours.order_by("time")
        )

        now = timezone.now()

        # 🔑 acha a previsão mais próxima do horário atual
        current_hour = None
        min_diff = None

        for h in hours:
            diff = abs((h.time - now).total_seconds())
            if min_diff is None or diff < min_diff:
                min_diff = diff
                current_hour = h

        ctx["hours"] = hours
        ctx["current_hour"] = current_hour

        return ctx