# members/views.py
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import UpdateView

from .forms import SignupForm, MemberUpdateForm
from .services import get_or_create_member_for_user


class SignupView(View):
    """
    Cadastro:
    - cria User
    - cria Member (via SignupForm.save)
    - loga automaticamente
    - redireciona para /auth/me/
    """
    def get(self, request):
        return render(request, "members/signup.html", {"form": SignupForm()})

    def post(self, request):
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("my_profile")
        return render(request, "members/signup.html", {"form": form})


class MyProfileView(LoginRequiredMixin, View):
    """
    Perfil do membro logado.
    Importante: usa get_or_create_member_for_user para nunca quebrar
    (ex: superuser/criação manual de usuário sem Member).
    """
    def get(self, request):
        member = get_or_create_member_for_user(request.user)
        catches = member.catches.select_related("species").order_by("-caught_at")
        return render(
            request,
            "members/my_profile.html",
            {"member": member, "catches": catches},
        )


class MyProfileEditView(LoginRequiredMixin, UpdateView):
    """
    Editar o perfil do membro logado.
    Importante: get_object garante Member existir.
    """
    form_class = MemberUpdateForm
    template_name = "members/my_profile_edit.html"

    def get_object(self, queryset=None):
        return get_or_create_member_for_user(self.request.user)

    def get_success_url(self):
        # você pode usar reverse() se preferir
        return "/auth/me/"
