#!/usr/bin/env python3
"""catalog.py: the local HyperFrames catalog, indexed and searchable. Pick from it before building anything custom.

  catalog.py build                      index $ENGINE/compositions (installed with `hyperframes add`) -> catalog.json
  catalog.py search captions chart      blocks/components whose name, tags or description match (all words)
  catalog.py search --tag lower-third   filter by tag; --type block|component; --json for machine output
  catalog.py show <name>                one item: file, composition id, variables, size, tags

The index records, for every item: name, type, src (relative to the compositions folder, i.e. a storyboard beat's
`src`), comp_id (`data-composition-id`, a beat's `comp_id`), variables (ids, types, defaults: a beat's `vars`),
tags and description from `hyperframes catalog --json`.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from html.parser import HTMLParser
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import runtime  # noqa: E402


def comp_dir() -> Path:
    configured = os.environ.get("VIDEO_COMPOSITIONS", "").strip()
    return (Path(configured).expanduser() if configured else runtime.find_engine_dir() / "compositions").resolve()


class Meta(HTMLParser):
    def __init__(self):
        super().__init__()
        self.root = None
        self.variables = []
        self.title = ""
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            self._in_title = True
        if a.get("data-composition-id") and self.root is None:
            self.root = {"comp_id": a["data-composition-id"], "width": a.get("data-width"),
                         "height": a.get("data-height"), "duration": a.get("data-duration")}
        if a.get("data-composition-variables"):
            try:
                value = json.loads(a["data-composition-variables"])
                for v in value if isinstance(value, list) else []:
                    if isinstance(v, dict) and v.get("id"):
                        self.variables.append({k: v.get(k) for k in ("id", "type", "label", "default") if k in v})
            except ValueError:
                pass

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data.strip()


def hyperframes_catalog() -> list[dict]:
    raw = comp_dir() / "catalog-raw.json"
    if raw.is_file():
        try:
            data = json.loads(raw.read_text(encoding="utf-8"))
            return data.get("results", data) if isinstance(data, dict) else data
        except ValueError:
            pass
    hf = runtime.find_engine_dir() / "node_modules" / ".bin" / ("hyperframes.cmd" if os.name == "nt" else "hyperframes")
    if hf.is_file():
        p = subprocess.run([str(hf), "catalog", "--json"], capture_output=True, text=True)
        if p.returncode == 0:
            try:
                data = json.loads(p.stdout)
                items = data.get("results", data) if isinstance(data, dict) else data
                raw.write_text(json.dumps(items, indent=1), encoding="utf-8")
                return items
            except ValueError:
                pass
    return []


def cmd_build(_a) -> int:
    base = comp_dir()
    if not base.is_dir():
        print(f"no compositions folder at {base}; run video-skills setup (it installs the HyperFrames catalog)")
        return 2
    info = {str(x.get("name")): x for x in hyperframes_catalog() if isinstance(x, dict) and x.get("name")}
    items = []
    html_files = [h for h in sorted(base.rglob("*.html")) if not any(part.startswith(".") for part in h.relative_to(base).parts)]
    print(f"  parsing and indexing {len(html_files)} HyperFrames composition files...")
    for html in html_files:
        rel = html.relative_to(base).as_posix()
        m = Meta()
        try:
            m.feed(html.read_text(encoding="utf-8", errors="replace"))
        except Exception:  # noqa: BLE001 - one broken file must not stop the index
            continue
        if not m.root:
            continue
        name = html.stem
        rec = info.get(name, {})
        tags = rec.get("tags") or rec.get("categories") or []
        if isinstance(tags, str):
            tags = [tags]
        items.append({
            "name": name,
            "type": rec.get("type") or ("component" if "components/" in rel else "block"),
            "src": rel,
            "comp_id": m.root["comp_id"],
            "variables": m.variables,
            "tags": [str(t) for t in tags],
            "description": rec.get("description") or rec.get("title") or m.title,
            "size": [m.root.get("width"), m.root.get("height")],
            "duration": m.root.get("duration"),
        })
    out = base / "catalog.json"
    out.write_text(json.dumps({"generated": time.strftime("%Y-%m-%d %H:%M"), "root": str(base), "count": len(items),
                               "items": items}, indent=1), encoding="utf-8")
    print(f"indexed {len(items)} HyperFrames blocks/components -> {out}")
    return 0 if items else 1


def load() -> list[dict]:
    path = comp_dir() / "catalog.json"
    if not path.is_file():
        raise SystemExit(f"no catalog index at {path}; run: catalog.py build")
    return json.loads(path.read_text(encoding="utf-8")).get("items", [])


def cmd_search(a) -> int:
    words = [w.lower() for w in a.words]
    hits = []
    for it in load():
        if a.type and it.get("type") != a.type:
            continue
        if a.tag and a.tag.lower() not in [t.lower() for t in it.get("tags", [])]:
            continue
        hay = " ".join([it["name"], " ".join(it.get("tags", [])), str(it.get("description") or "")]).lower()
        if all(w in hay for w in words):
            hits.append(it)
    hits = hits[: a.limit]
    if a.json:
        print(json.dumps(hits, indent=1))
        return 0
    for it in hits:
        var = ", ".join(v["id"] for v in it.get("variables", [])) or "-"
        print(f"{it['name']:<34} {it['type']:<9} tags: {', '.join(it.get('tags', [])) or '-'}")
        print(f"    src={it['src']}  comp_id={it['comp_id']}  vars: {var}")
        if it.get("description"):
            print(f"    {str(it['description'])[:140]}")
    print(f"{len(hits)} match(es)")
    return 0


def cmd_show(a) -> int:
    it = next((x for x in load() if x["name"] == a.name), None)
    if not it:
        print(f"{a.name}: not in the catalog index; try catalog.py search {a.name}")
        return 1
    print(json.dumps({**it, "file": str(comp_dir() / it["src"])}, indent=1))
    print("storyboard beat: " + json.dumps({"id": "b1", "type": "block", "src": it["src"], "comp_id": it["comp_id"],
                                            "vars": {v["id"]: v.get("default") for v in it.get("variables", [])},
                                            "in": 0.0, "out": 3.0, "refs": ["speech-001"]}))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build").set_defaults(f=cmd_build)
    s = sub.add_parser("search")
    s.add_argument("words", nargs="*")
    s.add_argument("--tag")
    s.add_argument("--type", choices=["block", "component"])
    s.add_argument("--limit", type=int, default=25)
    s.add_argument("--json", action="store_true")
    s.set_defaults(f=cmd_search)
    sh = sub.add_parser("show")
    sh.add_argument("name")
    sh.set_defaults(f=cmd_show)
    a = ap.parse_args()
    return a.f(a)


if __name__ == "__main__":
    raise SystemExit(main())
