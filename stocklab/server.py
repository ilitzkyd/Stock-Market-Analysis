"""A loopback-only local research app, not a public production web server."""

import argparse
import json
import logging
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import numpy as np

from .data import DataError
from .service import analyze, macro

ROOT = Path(__file__).resolve().parent
WORK = threading.Lock()


def encode(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    raise TypeError(f"Cannot serialize {type(value).__name__}.")


class Handler(BaseHTTPRequestHandler):
    def reply(self, status, data, kind="application/json; charset=utf-8"):
        content = (
            data
            if isinstance(data, bytes)
            else json.dumps(data, default=encode, allow_nan=False).encode()
        )
        self.send_response(status)
        for name, value in {
            "Content-Type": kind,
            "Content-Length": str(len(content)),
            "Cache-Control": "no-store",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' blob: data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'",
        }.items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(content)

    def local(self):
        port = self.server.server_port
        hosts = {f"127.0.0.1:{port}", f"localhost:{port}"}
        if self.headers.get("Host") not in hosts or (
            self.headers.get("Origin")
            and self.headers["Origin"] not in {f"http://{h}" for h in hosts}
        ):
            self.reply(403, {"error": "Open this app through its localhost address."})
            return False
        return True

    def do_GET(self):
        if not self.local():
            return
        if self.path in {"/", "/index.html"}:
            self.reply(200, (ROOT / "index.html").read_bytes(), "text/html; charset=utf-8")
        elif self.path == "/api/health":
            self.reply(200, {"app": "Stock Research Lab", "status": "ok"})
        elif self.path == "/favicon.ico":
            self.reply(204, b"")
        else:
            self.reply(404, {"error": "Not found."})

    def do_POST(self):
        if not self.local():
            return
        if self.path not in {"/api/analyze", "/api/macro"}:
            self.reply(404, {"error": "Not found."})
            return
        if self.headers.get("X-Stock-Lab") != "1":
            self.reply(403, {"error": "Use the Stock Research Lab app."})
            return
        if self.headers.get_content_type() != "application/json":
            self.reply(415, {"error": "Send application/json."})
            return
        try:
            size = int(self.headers.get("Content-Length", 0))
            if not 0 < size <= 4096:
                raise ValueError("Request must be 1-4096 bytes.")
            payload = json.loads(self.rfile.read(size))
        except (ValueError, UnicodeDecodeError) as error:
            self.reply(400, {"error": str(error)})
            return
        if not WORK.acquire(blocking=False):
            self.reply(429, {"error": "An analysis is already running. Please try again shortly."})
            return
        try:
            self.reply(200, analyze(payload) if self.path == "/api/analyze" else macro(payload))
        except DataError as error:
            self.reply(422, {"error": str(error)})
        except ValueError as error:
            self.reply(400, {"error": str(error)})
        except Exception:
            logging.exception("Analysis failed")
            self.reply(500, {"error": "Analysis failed. See the server terminal for details."})
        finally:
            WORK.release()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8766)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    with ThreadingHTTPServer(("127.0.0.1", args.port), Handler) as server:
        print(f"Stock Research Lab: http://127.0.0.1:{args.port}", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.", flush=True)


if __name__ == "__main__":
    main()
