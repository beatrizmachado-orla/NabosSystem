# weather/admin.py
from django.contrib import admin, messages
from django.urls import path
from django.shortcuts import redirect
from django.utils.html import format_html

from .models import (
    Spot,
    ForecastHour,
    StormglassRequestLog,
)

from .services.update_spot_forecast import update_spot_forecast

class ForecastHourInline(admin.TabularInline):
    model = ForecastHour
    extra = 0
    can_delete = True
    show_change_link = True
    ordering = ("time",)

    fields = (
        "time",
        "wave_height_m",
        "wave_period_s",
        "wave_direction_deg",
        "swell_height_m",
        "swell_period_s",
        "swell_direction_deg",
        "wind_speed_ms",
        "wind_direction_deg",
        "water_temp_c",
        "air_temp_c",
        "source",
    )


# =========================
# SPOT ADMIN
# =========================

@admin.register(Spot)
class SpotAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "latitude",
        "longitude",
        "last_forecast_update",
        "update_button",
    )

    readonly_fields = ("last_forecast_update",)
    inlines = [ForecastHourInline]

    # -------------------------
    # URL customizada
    # -------------------------
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:spot_id>/update-forecast/",
                self.admin_site.admin_view(self.update_forecast_view),
                name="weather-spot-update-forecast",
            )
        ]
        return custom_urls + urls

    # -------------------------
    # BOTÃO DE ATUALIZAÇÃO
    # -------------------------
    @admin.display(description="Previsão")
    def update_button(self, obj):
        return format_html(
            '<a class="button" href="{}">🔄 Atualizar</a>',
            f"{obj.id}/update-forecast/",
        )

    # -------------------------
    # VIEW DO BOTÃO
    # -------------------------
    def update_forecast_view(self, request, spot_id):
        spot = Spot.objects.get(id=spot_id)

        try:
            created = update_spot_forecast(spot)
            self.message_user(
                request,
                f"Previsão atualizada com sucesso ({created} horas novas).",
                messages.SUCCESS,
            )
        except Exception as e:
            self.message_user(
                request,
                f"Erro ao atualizar previsão: {e}",
                messages.ERROR,
            )

        return redirect("admin:weather_spot_changelist")


# =========================
# FORECAST HOUR ADMIN
# =========================

@admin.register(ForecastHour)
class ForecastHourAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "spot",
        "time",
        "wave_height_m",
        "wind_speed_ms",
        "water_temp_c",
        "source",
    )
    list_filter = ("spot", "source")
    search_fields = ("spot__name",)
    ordering = ("-time",)
    list_select_related = ("spot",)


# =========================
# REQUEST LOG ADMIN
# =========================

@admin.register(StormglassRequestLog)
class StormglassRequestLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "created_at",
        "spot",
        "status_code",
        "request_count",
        "daily_quota",
    )
    list_filter = ("status_code", "created_at")
    search_fields = ("spot__name",)
    ordering = ("-created_at",)
    list_select_related = ("spot",)
