"""Dashboard HTTP 服务与 SSE。"""

from __future__ import annotations

import json
import queue
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

STATIC_DIR = Path(__file__).resolve().parent / "static"


class StateHub:
    def __init__(self):
        self._lock = threading.Lock()
        self._snapshot: dict = {}
        self._subscribers: list[queue.Queue] = []

    def publish(self, snapshot: dict):
        with self._lock:
            self._snapshot = copy_snapshot(snapshot)
            for sub in self._subscribers:
                sub.put(self._snapshot)

    def snapshot(self) -> dict:
        with self._lock:
            return copy_snapshot(self._snapshot)

    def subscribe(self) -> queue.Queue:
        q: queue.Queue = queue.Queue()
        with self._lock:
            self._subscribers.append(q)
            if self._snapshot:
                q.put(self._snapshot)
        return q

    def unsubscribe(self, q: queue.Queue):
        with self._lock:
            if q in self._subscribers:
                self._subscribers.remove(q)


def copy_snapshot(data: dict) -> dict:
    return json.loads(json.dumps(data, ensure_ascii=False))


def make_handler(hub_ref: StateHub, graph_ref: dict):
    class DashboardHandler(BaseHTTPRequestHandler):
        hub = hub_ref
        graph = graph_ref

        def log_message(self, format, *args):
            return

        def _send_json(self, status: int, payload: dict):
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _send_bytes(self, status: int, body: bytes, content_type: str):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            path = urlparse(self.path).path
            if path in ("/", "/index.html"):
                file_path = STATIC_DIR / "index.html"
                if not file_path.is_file():
                    self._send_json(HTTPStatus.NOT_FOUND, {"error": "dashboard not found"})
                    return
                self._send_bytes(HTTPStatus.OK, file_path.read_bytes(), "text/html; charset=utf-8")
                return
            if path == "/api/graph":
                self._send_json(HTTPStatus.OK, self.graph)
                return
            if path == "/api/snapshot":
                self._send_json(HTTPStatus.OK, self.hub.snapshot())
                return
            if path == "/api/stream":
                self._handle_sse()
                return
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "not found"})

        def _handle_sse(self):
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.end_headers()

            sub = self.hub.subscribe()
            try:
                snap = self.hub.snapshot()
                if snap:
                    self._sse_write(snap)
                while True:
                    try:
                        item = sub.get(timeout=15)
                        self._sse_write(item)
                    except queue.Empty:
                        self.wfile.write(b": keepalive\n\n")
                        self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError, OSError):
                pass
            finally:
                self.hub.unsubscribe(sub)

        def _sse_write(self, payload: dict):
            data = json.dumps(payload, ensure_ascii=False)
            self.wfile.write(f"data: {data}\n\n".encode("utf-8"))
            self.wfile.flush()

    return DashboardHandler


class DashboardServer(ThreadingHTTPServer):
    allow_reuse_address = False

    def __init__(self, hub: StateHub, graph: dict, host: str, port: int):
        handler = make_handler(hub, graph)
        super().__init__((host, port), handler)
        self.url = f"http://{host}:{port}/"


def start_dashboard(hub: StateHub, graph: dict, port: int, host: str = "127.0.0.1") -> str:
    try:
        server = DashboardServer(hub, graph, host, port)
    except OSError as exc:
        winerr = getattr(exc, "winerror", None)
        if winerr == 10013:
            hint = f"dashboard 端口 {port} 无法绑定（权限/保留端口），请修改 DASHBOARD_PORT"
        else:
            hint = f"dashboard 端口 {port} 已被占用，请修改 DASHBOARD_PORT 或关闭占用进程"
        raise RuntimeError(hint) from exc

    thread = threading.Thread(target=server.serve_forever, name="gamebot-dashboard", daemon=True)
    thread.start()
    return server.url
