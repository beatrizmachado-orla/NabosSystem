from django.db import models

class Member(models.Model):
    photo = models.ImageField(upload_to="members/photos/", blank=True, null=True)
    name = models.CharField(max_length=120)
    age = models.PositiveIntegerField(blank=True, null=True)
    nickname = models.CharField(max_length=60, blank=True)
    bio = models.TextField("História", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.nickname or self.name
