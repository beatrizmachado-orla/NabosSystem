# weather/urls.py
from django.urls import path
from .views import SpotsListView, SpotDetailView

urlpatterns = [
    path("", SpotsListView.as_view(), name="spots_list"),
    path("<slug:slug>/", SpotDetailView.as_view(), name="spot_detail"),
]
