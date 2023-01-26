from django.contrib import messages
from django.views.generic import CreateView, UpdateView

from .forms import SiteUserCreateForm, SiteUserUpdateForm
from .models import SiteUser


class SiteUserCreateView(CreateView):
    model = SiteUser
    success_url = "/"
    form_class = SiteUserCreateForm


class SiteUserActionMixin:
    @property
    def success_msg(self):
        return NotImplemented

    def form_valid(self, form):
        messages.info(self.request, self.success_msg)
        return super().form_valid(form)


class SiteUserUpdateView(SiteUserActionMixin, UpdateView):
    model = SiteUser
    success_url = "/"
    success_msg = "User`s data updated!"
    form_class = SiteUserUpdateForm
