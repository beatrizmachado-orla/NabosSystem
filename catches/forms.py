from django import forms
from .models import Catch

class CatchCreateForm(forms.ModelForm):
    class Meta:
        model = Catch
        fields = ("photo", "species", "length_cm", "weight_kg", "location", "caught_at", "bait")
