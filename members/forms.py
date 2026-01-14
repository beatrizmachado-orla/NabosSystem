from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Member

class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    name = forms.CharField(max_length=120)
    nickname = forms.CharField(max_length=60, required=False)
    age = forms.IntegerField(required=False)
    bio = forms.CharField(required=False, widget=forms.Textarea)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "name", "nickname", "age", "bio")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            Member.objects.create(
                user=user,
                name=self.cleaned_data["name"],
                nickname=self.cleaned_data.get("nickname") or "",
                age=self.cleaned_data.get("age"),
                bio=self.cleaned_data.get("bio") or "",
            )
        return user


class MemberUpdateForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ("photo", "name", "age", "nickname", "bio")
        widgets = {"bio": forms.Textarea(attrs={"rows": 5})}
