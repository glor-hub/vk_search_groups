from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from vksearch.settings import DEBUG

from .view import index

urlpatterns = [
    path("", index, name="home"),
    path("vksearch/", include("vkgroup.urls", namespace="vkgroup")),
    path("siteauth/", include("siteauth.urls", namespace="siteauth")),
    path("admin/", admin.site.urls),
]

# ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if DEBUG:
    urlpatterns += (path("__debug__/", include("debug_toolbar.urls")),)
if DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
