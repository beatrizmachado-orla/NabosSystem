from django.contrib.auth import get_user_model
from .models import Member

User = get_user_model()

def get_or_create_member_for_user(user: User) -> Member:
    member, _ = Member.objects.get_or_create(
        user=user,
        defaults={
            "name": user.get_username(),
            "nickname": "",
            "bio": "",
        },
    )
    return member
