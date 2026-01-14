from django.contrib import admin
from .models import Supporter


@admin.register(Supporter)
class SupporterAdmin(admin.ModelAdmin):
    list_display = ("is_active", "name", "website",)
    list_display_links = ("name",)
    list_editable = ("is_active",)
    search_fields = ("name", "website")