from django.contrib import admin
from django.utils.html import format_html
from .models import Member


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = (
        "photo_thumb",
        "name",
        "nickname",
        "age",
        "gender",
        "user",
        "created_at",
    )

    search_fields = (
        "name",
        "nickname",
        "user__username",
        "user__email",
    )

    list_filter = ("gender",)

    list_select_related = ("user",)

    ordering = ("name",)

    @admin.display(description="Foto")
    def photo_thumb(self, obj: Member):
        if obj.photo:
            return format_html(
                '<img src="{}" style="width:60px; height:60px; '
                'object-fit:cover; border-radius:80%;" />',
                obj.photo.url,
            )
        return "Sem Foto"
