from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

from .views import SignupView, MyProfileView, MyProfileEditView

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", LoginView.as_view(template_name="members/login.html"), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),

    path("me/", MyProfileView.as_view(), name="my_profile"),
    path("me/edit/", MyProfileEditView.as_view(), name="my_profile_edit"),
]
