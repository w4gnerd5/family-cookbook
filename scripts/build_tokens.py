#!/usr/bin/env python3
"""Generate print/tokens.typ and web/tokens.css from tokens.yaml."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def parse_simple_yaml(text):
    """Parse the flat two-level YAML in tokens.yaml (no external deps)."""
    data, group = {}, None
    for line in text.splitlines():
        line = re.sub(r"(^|\s)#\s.*$", "", line).rstrip()
        if not line.strip():
            continue
        if not line.startswith(" "):
            group = line.rstrip(":")
            data[group] = {}
        else:
            key, val = line.strip().split(":", 1)
            val = val.strip().strip('"')
            try:
                val = float(val) if "." in val else int(val)
            except ValueError:
                pass
            data[group][key] = val
    return data


def typ_value(v):
    if isinstance(v, str):
        if re.fullmatch(r"#\w{6}", v):
            return f'rgb("{v}")'
        return f'"{v}"'
    return str(v)


def main():
    t = parse_simple_yaml((ROOT / "tokens.yaml").read_text())

    lines = ["// GENERATED from tokens.yaml — do not edit by hand."]
    for group, kv in t.items():
        for k, v in kv.items():
            unit = ""
            pct = group == "card" and k.startswith("title_col")
            if (group in ("size", "card") and not pct) or (group == "space" and k != "tracking"):
                unit = "pt"
            if group == "label" and k == "tracking":
                unit = "em"
            val = f"{v}%" if pct else f"{typ_value(v)}{unit}"
            lines.append(f"#let {group}-{k.replace('_', '-')} = {val}")
    (ROOT / "print").mkdir(exist_ok=True)
    (ROOT / "print" / "tokens.typ").write_text("\n".join(lines) + "\n")

    css = [":root {  /* GENERATED from tokens.yaml — do not edit by hand. */"]
    for group, kv in t.items():
        for k, v in kv.items():
            name = f"--{group}-{k.replace('_', '-')}"
            if group == "font":
                v = f"'{v}'"
            elif group == "size":
                v = f"{v / 12:.3f}rem"  # 12pt print body ~ 1rem web
            elif group == "card" and str(k).startswith("title_col"):
                v = f"{v}%"
            elif group == "card" or (group == "space" and k != "tracking"):
                v = f"{v}pt"
            elif group == "label" and k == "tracking":
                v = f"{v}em"
            css.append(f"  {name}: {v};")
    css.append("}")
    (ROOT / "web").mkdir(exist_ok=True)
    (ROOT / "web" / "tokens.css").write_text("\n".join(css) + "\n")
    print("wrote print/tokens.typ and web/tokens.css")


if __name__ == "__main__":
    main()
