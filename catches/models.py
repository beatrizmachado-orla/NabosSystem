from decimal import Decimal
from django.db import models
from django.utils.text import slugify
from members.models import Member


class Species(models.Model):
    name = models.CharField("Nome comum", max_length=120, unique=True)
    slug = models.SlugField("Slug", max_length=140, unique=True, blank=True)

    scientific_name = models.CharField("Nome científico", max_length=160, blank=True, null=True)
    summary = models.TextField("Resumo", blank=True, null=True)
    image_url = models.URLField("Imagem (URL)", blank=True, null=True)

    wikipedia_title = models.CharField("Título na Wikipedia", max_length=200, blank=True, null=True)
    fishbase_id = models.IntegerField("FishBase ID", null=True, blank=True)

    min_length_cm = models.DecimalField("Comprimento mínimo (cm)", max_digits=6, decimal_places=2, default=0)
    points_per_cm = models.DecimalField("Pontos por centímetro", max_digits=6, decimal_places=2, default=0)

    behavior = models.TextField("Comportamento", blank=True, null=True)
    habitats = models.TextField("Locais / Habitat", blank=True, null=True)
    is_competition_allowed = models.BooleanField("Aceita na competição", default=True)
    
    best_times = models.CharField("Melhor horário/condição", max_length=180, blank=True, null=True)

    updated_at = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        verbose_name = "Espécie"
        verbose_name_plural = "Espécies"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Species.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Catch(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="catches", verbose_name="Membro")
    species = models.ForeignKey(Species, on_delete=models.PROTECT, related_name="catches", verbose_name="Espécie")

    photo = models.ImageField("Foto", upload_to="catches/photos/", blank=True, null=True)

    length_cm = models.DecimalField("Tamanho (cm)", max_digits=6, decimal_places=2)
    weight_kg = models.DecimalField("Peso (kg)", max_digits=6, decimal_places=2)

    location = models.CharField("Local", max_length=150)
    bait = models.CharField("Isca", max_length=150, blank=True, null=True)

    caught_at = models.DateTimeField("Data da captura")
    created_at = models.DateTimeField("Registrado em", auto_now_add=True)

    class Meta:
        verbose_name = "Captura"
        verbose_name_plural = "Capturas"
        ordering = ["-caught_at"]

    def __str__(self):
        return f"{self.member} - {self.species} ({self.caught_at:%d/%m/%Y})"

    def calc_points(self) -> int:
        """
        Regra:
        - Só pontua se length_cm >= species.min_length_cm
        - Pontos = length_cm * species.points_per_cm
        - Retorna inteiro (arredondando para baixo)
        """
        if self.length_cm is None or self.species_id is None:
            return 0

        min_len = self.species.min_length_cm or Decimal("0")
        mult = self.species.points_per_cm or Decimal("0")

        if self.length_cm < min_len:
            return 0

        pts = self.length_cm * mult
        return int(pts)

    @property
    def points_int(self) -> int:
        """Atalho para usar em templates/admin sem formatação Decimal."""
        return self.calc_points()


class SpeciesPhoto(models.Model):
    species = models.ForeignKey(Species, on_delete=models.CASCADE, related_name="photos", verbose_name="Espécie")
    image = models.ImageField("Foto", upload_to="species/photos/")
    caption = models.CharField("Legenda", max_length=140, blank=True, null=True)
    created_at = models.DateTimeField("Criado em", auto_now_add=True)

    class Meta:
        verbose_name = "Foto da espécie"
        verbose_name_plural = "Fotos das espécies"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.species} - {self.caption or 'Foto'}"


class SpeciesBaitIdea(models.Model):
    species = models.ForeignKey(Species, on_delete=models.CASCADE, related_name="bait_ideas", verbose_name="Espécie")
    bait_name = models.CharField("Isca / Técnica", max_length=120)
    notes = models.TextField("Dicas", blank=True, null=True)

    class Meta:
        verbose_name = "Isca indicada"
        verbose_name_plural = "Iscas indicadas"
        ordering = ["bait_name"]

    def __str__(self):
        return f"{self.species} - {self.bait_name}"
