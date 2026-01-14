from django.db import models
from django.utils import timezone
from django.utils.text import slugify

class Spot(models.Model):
    name = models.CharField("Nome", max_length=120)
    slug = models.SlugField("Slug", max_length=140, unique=True, blank=True)

    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    last_forecast_update = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Spot de pesca"
        verbose_name_plural = "Spots de pesca"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            slug = base
            i = 1
            while Spot.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class ForecastHour(models.Model):
    """
    Previsão HORÁRIA normalizada (1 linha = 1 hora)
    """
    spot = models.ForeignKey(
        Spot,
        on_delete=models.CASCADE,
        related_name="forecast_hours",
        verbose_name="Spot"
    )

    time = models.DateTimeField("Hora (UTC)")

    # 🌬️ Vento
    wind_speed_ms = models.FloatField("Vento (m/s)", null=True, blank=True)
    wind_direction_deg = models.IntegerField("Direção do vento (°)", null=True, blank=True)
    gust_ms = models.FloatField("Rajada (m/s)", null=True, blank=True)

    # 🌊 Ondas
    wave_height_m = models.FloatField("Altura da onda (m)", null=True, blank=True)
    wave_period_s = models.FloatField("Período da onda (s)", null=True, blank=True)
    wave_direction_deg = models.IntegerField("Direção da onda (°)", null=True, blank=True)

    # 🌊 Swell
    swell_height_m = models.FloatField("Altura do swell (m)", null=True, blank=True)
    swell_period_s = models.FloatField("Período do swell (s)", null=True, blank=True)
    swell_direction_deg = models.IntegerField("Direção do swell (°)", null=True, blank=True)

    # 🌡️ Temperaturas
    water_temp_c = models.FloatField("Temp. da água (°C)", null=True, blank=True)
    air_temp_c = models.FloatField("Temp. do ar (°C)", null=True, blank=True)

    # Fonte usada (NOAA, METEO, etc.)
    source = models.CharField("Fonte", max_length=30, default="noaa")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Previsão horária"
        verbose_name_plural = "Previsões horárias"
        ordering = ["spot", "time"]
        unique_together = ("spot", "time")

    def __str__(self):
        return f"{self.spot} • {self.time:%d/%m %Hh}"

class StormglassRequestLog(models.Model):
    """
    Log de chamadas à API (controle das 10 req/dia)
    """
    created_at = models.DateTimeField(auto_now_add=True)

    spot = models.ForeignKey(
        Spot,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Spot"
    )

    status_code = models.IntegerField("Status HTTP", null=True, blank=True)

    request_count = models.IntegerField("Requests usados hoje", null=True, blank=True)
    daily_quota = models.IntegerField("Quota diária", null=True, blank=True)

    error_message = models.TextField("Erro", blank=True, null=True)

    class Meta:
        verbose_name = "Log Stormglass"
        verbose_name_plural = "Logs Stormglass"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.created_at:%d/%m %H:%M} • {self.status_code}"
