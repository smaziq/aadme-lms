from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404
from django.views import View


class SpaIndexView(View):
    """Serve the Vite SPA index for client-side routes."""

    def get(self, request, *_args, **_kwargs):
        index = Path(settings.FRONTEND_DIST_DIR) / "index.html"
        if not index.is_file():
            raise Http404("SPA build not found")
        return FileResponse(index.open("rb"), content_type="text/html")
