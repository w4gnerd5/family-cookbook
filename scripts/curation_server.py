#!/usr/bin/env python3
"""Live curation dashboard. Serves a sortable/filterable table over
curation-state.json; edits POST back and write the file immediately.
The page polls and re-renders when the file changes (e.g. when Claude
stamps a status), so it can stay open indefinitely.

Run: python3 scripts/curation_server.py   (port 8765)
"""
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "curation-state.json"
LOCK = threading.Lock()
PAGE = (ROOT / "scripts" / "curation_page.html").read_bytes()


def load():
    return json.loads(STATE.read_text())


def save(state):
    tmp = STATE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=1))
    tmp.replace(STATE)


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/":
            self._send(200, PAGE, "text/html; charset=utf-8")
        elif self.path.startswith("/state"):
            with LOCK:
                mtime = STATE.stat().st_mtime_ns
                body = json.dumps({"mtime": mtime, "state": load()}).encode()
            self._send(200, body)
        else:
            self._send(404, b"{}")

    def do_POST(self):
        if self.path != "/update":
            return self._send(404, b"{}")
        n = int(self.headers.get("Content-Length", 0))
        upd = json.loads(self.rfile.read(n))
        # {"kind": "inventory|merges|questions", "id": ..., "field": ..., "value": ...}
        editable = {
            "inventory": {"new_section", "new_order", "cut", "notes"},
            "merges": {"decision", "notes"},
            "questions": {"answer"},
        }
        with LOCK:
            state = load()
            rows = state[upd["kind"]]
            keyfield = {"inventory": "id", "merges": "group", "questions": "id"}[upd["kind"]]
            row = next(r for r in rows if r[keyfield] == upd["id"])
            if upd["field"] not in editable[upd["kind"]]:
                return self._send(403, b'{"error":"field not editable"}')
            row[upd["field"]] = upd["value"]
            save(state)
            mtime = STATE.stat().st_mtime_ns
        self._send(200, json.dumps({"ok": True, "mtime": mtime}).encode())


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", 8765), H).serve_forever()
