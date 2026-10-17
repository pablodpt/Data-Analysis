"""Serve Marketwatch locally, either from this repo or as a flat app folder."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
import os

HERE = Path(__file__).resolve().parent
# In this repository, serve the root redirect and /market-watch/ app route.
# In a downloaded flat package, serve the app directly from its own folder.
IS_REPO_APP = (HERE.parent / "index.html").is_file() and (HERE.parent / "market-watch").is_dir()
ROOT = HERE.parent if IS_REPO_APP else HERE
APP = HERE


class PreviewHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def translate_path(self, path):
        request_path = urlsplit(path).path
        if request_path == "/favicon.ico":
            return str(APP / "favicon.svg")
        target = Path(super().translate_path(request_path))
        if target.is_file() or target.is_dir():
            return str(target)
        # Keep unknown document routes on the dashboard instead of a server 404.
        fallback = ROOT / "index.html" if IS_REPO_APP else APP / "index.html"
        return str(fallback)

    def guess_type(self, path):
        if path.endswith("favicon.svg"):
            return "image/svg+xml"
        return super().guess_type(path)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    print(f"Marketwatch preview listening on 0.0.0.0:{port}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", port), PreviewHandler).serve_forever()
