# -*- coding: utf-8 -*-
"""
server.py — Interactive Stock Research Agent web app (stdlib only).

Routes:
  GET  /                  web UI (search any ticker / company name)
  GET  /api/profiles      KB ticker list (JSON)
  GET  /api/reports       list of generated reports (JSON)
  POST /api/research      {ticker, name?} -> runs the 7-stage pipeline,
                          saves the HTML report, returns a JSON summary
  GET  /reports/<file>    serves a generated standalone HTML report

Run:  python -m stock_research_agent serve  (default 0.0.0.0:8000)
"""
from __future__ import annotations

import io
import json
import os
import re
import sys
import urllib.parse
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from stock_research_agent import research, report_html, knowledge_base  # noqa: E402

REPORTS_DIR = os.path.join(HERE, "reports")
WEB_DIR = os.path.join(HERE, "web")


def do_research(ticker: str, name: str = "") -> dict:
    result = research.run(ticker if ticker else name)
    html = report_html.build(result)
    path = research.save_report(result, html)
    meta = result["meta"]
    v = result["verdict"]
    return dict(
        ok=True,
        ticker=meta["ticker"],
        name=meta["name"],
        file=os.path.basename(path),
        url=f"/reports/{os.path.basename(path)}",
        price=meta["price"],
        currency=meta["currency"],
        verdict=v["label"],
        composite=v["composite"],
        fair_value=v["iv"],
        upside=result["stages"]["fundamentals"]["upside"],
        data_quality=meta["data_quality"],
        worth=v["worth"],
    )


class Handler(BaseHTTPRequestHandler):
    server_version = "StockResearchAgent/2.0"

    def _send(self, code: int, body: bytes, ctype: str):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, obj, code: int = 200):
        self._send(code, json.dumps(obj, ensure_ascii=False).encode("utf-8"),
                   "application/json; charset=utf-8")

    def _file(self, path: str, ctype: str):
        try:
            with open(path, "rb") as fh:
                self._send(200, fh.read(), ctype)
        except FileNotFoundError:
            self._json({"ok": False, "error": "not found"}, 404)

    def log_message(self, fmt, *args):  # keep preview logs quiet
        sys.stderr.write("[sra] " + (fmt % args) + "\n")

    def do_GET(self):
        p = urllib.parse.urlparse(self.path).path
        if p in ("/", "/index.html"):
            self._file(os.path.join(WEB_DIR, "index.html"), "text/html; charset=utf-8")
        elif p == "/api/profiles":
            self._json({"ok": True, "profiles": knowledge_base.list_profiles()})
        elif p == "/api/reports":
            items = []
            if os.path.isdir(REPORTS_DIR):
                for f in sorted(os.listdir(REPORTS_DIR), reverse=True):
                    if f.endswith(".html"):
                        items.append(dict(file=f,
                                          mtime=os.path.getmtime(os.path.join(REPORTS_DIR, f))))
            self._json({"ok": True, "reports": items})
        elif p == "/api/reports/zip":
            if not os.path.isdir(REPORTS_DIR) or not any(
                    f.endswith(".html") for f in os.listdir(REPORTS_DIR)):
                self._json({"ok": False, "error": "no reports yet"}, 404)
                return
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
                for f in sorted(os.listdir(REPORTS_DIR)):
                    if f.endswith(".html"):
                        z.write(os.path.join(REPORTS_DIR, f), f)
            data = buf.getvalue()
            self.send_response(200)
            self.send_header("Content-Type", "application/zip")
            self.send_header("Content-Disposition",
                             'attachment; filename="stock_research_reports.zip"')
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)
        elif p.startswith("/reports/"):
            name = os.path.basename(p)
            if name.endswith(".html"):
                self._file(os.path.join(REPORTS_DIR, name), "text/html; charset=utf-8")
            else:
                self._json({"ok": False, "error": "bad file"}, 400)
        else:
            self._json({"ok": False, "error": "not found"}, 404)

    def do_POST(self):
        p = urllib.parse.urlparse(self.path).path
        if p == "/api/research":
            try:
                ln = int(self.headers.get("Content-Length", 0))
                body = json.loads(self.rfile.read(ln) or b"{}")
                ticker = (body.get("ticker") or "").strip()
                name = (body.get("name") or "").strip()
                if not ticker and not name:
                    self._json({"ok": False, "error": "provide a ticker or company name"}, 400)
                    return
                out = do_research(ticker, name)
                self._json(out)
            except Exception as e:  # noqa: BLE001
                self._json({"ok": False, "error": str(e)}, 500)
        else:
            self._json({"ok": False, "error": "not found"}, 404)


def serve(host: str = "0.0.0.0", port: int = 8000):
    os.makedirs(REPORTS_DIR, exist_ok=True)
    httpd = ThreadingHTTPServer((host, port), Handler)
    print(f"Stock Research Agent web app: http://{host}:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    serve()
