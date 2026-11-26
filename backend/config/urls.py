from django.contrib import admin
from django.urls import include, path
from django.http import JsonResponse

def health(_request):
    return JsonResponse({"status": "ok"})

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health),
    path("api/auth/", include("accounts.urls")),
    path("api/admin/", include("catalog.urls")),
]