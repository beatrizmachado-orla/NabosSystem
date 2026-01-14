from django.core.management.base import BaseCommand
from catches.models import Species
from django.utils.text import slugify

RULES = [
    # CATEGORIA A (30)
    ("ROBALO FLECHA", 50, 30, "A"),
    ("ROBALO PEVA", 35, 30, "A"),
    ("PESCADA AMARELA", 40, 30, "A"),
    ("PAMPO / SARNAMBIGUARA", 30, 30, "A"),
    ("LINGUADO", 35, 30, "A"),
    ("ANCHOVA", 35, 30, "A"),

    # CATEGORIA B (20)
    ("PESCADA BRANCA", 30, 20, "B"),
    ("PIRAÚNA", 40, 20, "B"),
    ("SARGO", 35, 20, "B"),
    ("XARÉU AMARELO", 30, 20, "B"),
    ("XARÉU BRANCO / GALO PENACHO", 30, 20, "B"),

    # CATEGORIA C (10)
    ("CORVINA", 30, 10, "C"),
    ("BAIACÚ", 30, 10, "C"),
    ("GUAIVIRA", 40, 10, "C"),
    ("FAQUECO", 25, 10, "C"),
    ("XERELETE", 25, 10, "C"),
    ("GALO", 25, 10, "C"),
]

class Command(BaseCommand):
    help = "Cria/atualiza espécies com regra oficial (mínimo e pontos por cm)"

    def handle(self, *args, **kwargs):
        for name, min_cm, ppc, cat in RULES:
            obj, _ = Species.objects.get_or_create(name=name)
            obj.min_length_cm = min_cm
            obj.points_per_cm = ppc
            obj.category = cat
            if not obj.slug:
                obj.slug = slugify(obj.name)
            obj.save()
        self.stdout.write(self.style.SUCCESS("Espécies atualizadas com regras oficiais."))
