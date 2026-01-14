from django.urls import path
from . import views

urlpatterns = [
    path("new/", views.CatchCreateView.as_view(), name="catch_new"),
    path("<int:pk>/", views.CatchDetailView.as_view(), name="catch_detail"),
    path("competicao/especies/", views.CompetitionSpeciesListView.as_view(), name="competition_species_list"),
    path("especies/<slug:slug>/", views.SpeciesDetailView.as_view(), name="species_detail"),
]
