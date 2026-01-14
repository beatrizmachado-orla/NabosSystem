from django.db import models
from django.contrib.auth.models import User


class Member(models.Model):
    GENDER_CHOICES = [
        ("F", "Feminino"),
        ("M", "Masculino"),
        ("O", "Outro / Prefiro não dizer"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    nickname = models.CharField(max_length=60, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)

    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        default="O",
    )

    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to="members/photos/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
