from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path, re_path

from config.spa import SpaIndexView


def health(_request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health),
    path("api/auth/", include("accounts.urls")),
    path("api/admin/", include("catalog.urls")),
    path("api/admin/", include("learning.urls")),
    path("api/me/", include("learning.student_urls")),
    # SPA catch-all (API/admin/static handled above / by WhiteNoise for /assets)
    re_path(r"^(?!api/|admin/|static/).*$", SpaIndexView.as_view(), name="spa"),
]
