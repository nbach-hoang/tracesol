"""Local-only HTTP server for TraceSol. Python 3.10+, standard library only."""
import argparse
import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from tracesol.engine import InputError, analyze, export_csv, parse_csv

ROOT = Path(__file__).resolve().parent
WEB = ROOT / "web"
MAX_BODY = 2_500_000


class Handler(BaseHTTPRequestHandler):
    server_version = "TraceSol/1.0"

    def log_message(self, *args):
        pass  # Uploaded evidence never appears in logs.

    def reply(self, status, body, kind="application/json; charset=utf-8"):
        if not isinstance(body, bytes):
            body = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'self'; img-src 'self' data: blob:; style-src 'self' 'unsafe-inline'; script-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(body)

    def error_json(self, status, message):
        self.reply(status, json.dumps({"error": message}))

    def allowed_host(self):
        return self.headers.get("Host") in {f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}"}

    def do_GET(self):
        if not self.allowed_host():
            return self.error_json(403, "Use the localhost address printed by TraceSol.")
        route = urlsplit(self.path).path
        if route == "/api/health":
            return self.reply(200, json.dumps({"ok": True, "version": "1.0.0"}))
        if route == "/api/demo":
            return self.reply(200, json.dumps({"csv": (ROOT / "data/demo.csv").read_text(encoding="utf-8"), "label": "Synthetic teaching examples, not measured or published values"}))
        public = {"/": "index.html", "/index.html": "index.html", "/app.js": "app.js", "/style.css": "style.css", "/favicon.svg": "favicon.svg"}
        if route not in public:
            return self.error_json(404, "Page not found.")
        path = WEB / public[route]
        self.reply(200, path.read_bytes(), mimetypes.guess_type(str(path))[0] or "application/octet-stream")

    def do_POST(self):
        if not self.allowed_host():
            return self.error_json(403, "Invalid host.")
        route = urlsplit(self.path).path
        if route not in {"/api/analyze", "/api/export/csv"}:
            return self.error_json(404, "Endpoint not found.")
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > MAX_BODY:
                return self.error_json(413, "Request must be non-empty and smaller than 2.5 MB.")
            body = self.rfile.read(length)
            origin = self.headers.get("Origin")
            if origin and origin not in {f"http://127.0.0.1:{self.server.server_port}", f"http://localhost:{self.server.server_port}"}:
                return self.error_json(403, "Cross-origin requests are not allowed.")
            payload = json.loads(body)
            if not isinstance(payload, dict):
                raise InputError("Request must be a JSON object.")
            rows = parse_csv(payload["csv"]) if "csv" in payload else payload.get("rows")
            report = analyze(rows, payload.get("threshold", 0.5), payload.get("reviews", {}))
            if route == "/api/export/csv":
                return self.reply(200, export_csv(report), "text/csv; charset=utf-8")
            self.reply(200, json.dumps(report, allow_nan=False))
        except (InputError, ValueError, UnicodeError, TypeError) as exc:
            self.error_json(400, str(exc))


def main():
    parser = argparse.ArgumentParser(description="TraceSol: local solubility evidence review")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--audit", type=Path, help="Audit a CSV without opening the app")
    parser.add_argument("--output", type=Path, help="Save a CLI audit as JSON")
    args = parser.parse_args()
    if args.audit:
        try:
            report = analyze(parse_csv(args.audit.read_text(encoding="utf-8-sig")))
        except (OSError, InputError) as exc:
            parser.error(str(exc))
        output = json.dumps(report, indent=2, ensure_ascii=False)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(output, encoding="utf-8")
        else:
            print(output)
        return
    try:
        server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
        server.daemon_threads = True
    except OSError as exc:
        parser.exit(1, f"Could not start: {exc}. Try --port 8766.\n")
    print(f"TraceSol is ready: http://127.0.0.1:{server.server_port}\nLocal processing. No accounts or API keys. Press Ctrl+C to stop.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
