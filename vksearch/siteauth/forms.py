from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import SiteUser


class SiteUserCreateForm(UserCreationForm):
    class Meta:
        model = SiteUser
        fields = ("username", "email", "password1", "password2")


class SiteUserUpdateForm(UserChangeForm):
    password = None

    class Meta:
        model = SiteUser
        fields = ("username", "email")
