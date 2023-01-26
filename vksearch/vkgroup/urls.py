from django.urls import path

from .views import communities_view

app_name = "vkgroup"

urlpatterns = [
    path("", communities_view, name="search"),
]
