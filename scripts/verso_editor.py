#!/usr/bin/env python3
"""Verso art-direction editor. Serves a drag/rotate/scale/z editor over the
band and snapshot verso layouts; edits POST back and rewrite the scans: block
of the recipe's .md frontmatter, then md_to_data.py refreshes recipes.json.

The page replicates cookbook.typ's card geometry in CSS transforms. It is a
placement tool, not a proof: the compiled PDF stays the referee.

Run: python3 scripts/verso_editor.py   (port 8766)
"""
import json
import re
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent.parent
LOCK = threading.Lock()
PAGE = ROOT / "scripts" / "verso_editor.html"

# fields a card entry may carry, in the order they are written
FIELDS = ["scale", "tilt", "z", "dx", "dy", "exposure", "hide"]
DEFAULTS = {"scale": 1.0, "dx": 0.0, "dy": 0.0}


def fmt(v):
    if isinstance(v, float) and v == int(v):
        return str(int(v))
    if isinstance(v, float):
        return str(round(v, 2))
    return str(v)


def parse_scan_block(fm_lines):
    """Return (start, end, entries) for the scans: block inside frontmatter
    lines; entries are (path, {field: raw_value}) preserving unknown fields."""
    start = next(i for i, l in enumerate(fm_lines) if re.match(r"^scans:\s*$", l))
    end = start + 1
    entries = []
    while end < len(fm_lines):
        l = fm_lines[end]
        if re.match(r"^  - ", l):
            item = l[4:].strip()
            if item.startswith("path:"):
                entries.append([item.split(":", 1)[1].strip().strip('"'), {}])
            else:
                entries.append([item.strip('"'), {}])
        elif re.match(r"^    \S", l) and entries:
            k, v = l.strip().split(":", 1)
            entries[-1][1][k.strip()] = v.strip().strip('"')
        else:
            break
        end += 1
    return start, end, entries


def save_updates(relfile, updates):
    """updates: {path: {field: value|None}} — None deletes the field.
    Untouched entries are preserved verbatim in spirit (re-emitted from their
    parsed fields); values equal to defaults are dropped."""
    p = ROOT / relfile
    text = p.read_text()
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    fm_lines = m.group(1).split("\n")
    start, end, entries = parse_scan_block(fm_lines)

    out = ["scans:"]
    for path, fields in entries:
        if path in updates:
            for k, v in updates[path].items():
                if v is None:
                    fields.pop(k, None)
                else:
                    fields[k] = v
            # drop values that equal the layout defaults
            for k, d in DEFAULTS.items():
                if k in fields and abs(float(fields[k]) - d) < 1e-9:
                    del fields[k]
        if fields:
            out.append(f"  - path: {path}")
            for k in FIELDS:
                if k in fields:
                    out.append(f"    {k}: {fmt(fields[k])}")
            for k in fields:                    # unknown fields survive, last
                if k not in FIELDS:
                    out.append(f"    {k}: {fields[k]}")
        else:
            out.append(f"  - {path}")

    fm_lines[start:end] = out
    p.write_text("---\n" + "\n".join(fm_lines) + "\n---\n" + text[m.end():])
    subprocess.run(["python3", "scripts/md_to_data.py"], cwd=ROOT, check=True,
                   capture_output=True)


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
        elif u.path == "/recipes":
            data = {
                "recipes": json.loads((ROOT / "print" / "recipes.json").read_text()),
                "tokens": {k: v for k, v in re.findall(
                    r"#let (\S+) = ([\d.]+)pt", (ROOT / "print" / "tokens.typ").read_text())},
            }
            self._send(200, json.dumps(data).encode())
        elif u.path == "/file":
            rel = parse_qs(u.query).get("p", [""])[0]
            f = (ROOT / rel).resolve()
            ok = f.is_relative_to(ROOT / "print" / "cards") or f.is_relative_to(ROOT / "assets")
            if ok and f.is_file():
                ctype = "image/png" if f.suffix == ".png" else "image/jpeg"
                self._send(200, f.read_bytes(), ctype)
            else:
                self._send(404, b"{}")
        else:
            self._send(404, b"{}")

    def do_POST(self):
        if self.path != "/save":
            return self._send(404, b"{}")
        n = int(self.headers.get("Content-Length", 0))
        req = json.loads(self.rfile.read(n))
        with LOCK:
            save_updates(req["file"], req["updates"])
        self._send(200, b'{"ok": true}')


if __name__ == "__main__":
    print("verso editor: http://localhost:8766")
    ThreadingHTTPServer(("127.0.0.1", 8766), H).serve_forever()
