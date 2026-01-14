from django.db import models


class Supporter(models.Model):
    name = models.CharField(max_length=120)
    logo = models.ImageField(upload_to="supporters/logos/", blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("order", "name")

    def __str__(self):
        return self.name
