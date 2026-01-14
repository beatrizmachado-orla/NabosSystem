from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("grupo/", views.group, name="group"),
    path("grupo/<int:pk>/", views.member_detail, name="member_detail"),
    path("apoiadores/", views.supporters, name="supporters"),
    path("ranking/", views.ranking, name="ranking"),
]
