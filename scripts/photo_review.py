#!/usr/bin/env python3
"""Photo-review dashboard. Serves photo-review.json (git-tracked ledger) as a
per-recipe, per-round review table: candidate thumbnails linking to their
source pages, the current dish photo, a notes field per round for Paul, and an
after-action comment per round written by Claude. Rounds are append-only.

Run: python3 scripts/photo_review.py   (port 8767)
"""
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "photo-review.json"
LOCK = threading.Lock()
PAGE = ROOT / "scripts" / "photo_review.html"


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
        u = urlparse(self.path)
        if u.path == "/":
            self._send(200, PAGE.read_bytes(), "text/html; charset=utf-8")
        elif u.path == "/state":
            with LOCK:
                body = json.dumps({"mtime": STATE.stat().st_mtime_ns, "state": load()}).encode()
            self._send(200, body)
        elif u.path == "/file":
            rel = parse_qs(u.query).get("p", [""])[0]
            f = (ROOT / rel).resolve()
            ok = (f.is_relative_to(ROOT / "print" / "photo-cands")
                  or f.is_relative_to(ROOT / "assets"))
            if ok and f.is_file():
                ctype = "image/png" if f.suffix == ".png" else "image/jpeg"
                self._send(200, f.read_bytes(), ctype)
            else:
                self._send(404, b"{}")
        else:
            self._send(404, b"{}")

    def do_POST(self):
        # {"img": ..., "field": "status"} or {"img": ..., "round": n, "field": "user_note", "value": ...}
        if self.path != "/update":
            return self._send(404, b"{}")
        n = int(self.headers.get("Content-Length", 0))
        upd = json.loads(self.rfile.read(n))
        with LOCK:
            state = load()
            rec = next((r for r in state["recipes"] if r["img"] == upd["img"]), None)
            if rec is None:
                return self._send(404, b'{"error": "unknown recipe"}')
            if upd["field"] == "status":
                rec["status"] = str(upd["value"])[:40]
            elif upd["field"] == "user_note":
                rnd = next((r for r in rec["rounds"] if r["n"] == upd["round"]), None)
                if rnd is None:
                    return self._send(404, b'{"error": "unknown round"}')
                rnd["user_note"] = str(upd["value"])[:4000]
            else:
                return self._send(400, b'{"error": "field not editable"}')
            save(state)
        self._send(200, b'{"ok": true}')


if __name__ == "__main__":
    print("photo review: http://localhost:8767")
    ThreadingHTTPServer(("127.0.0.1", 8767), H).serve_forever()
