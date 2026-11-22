"""Read-only access to the OSA spec text, JSON Schemas and conformance fixtures, and document validation.

Files come from the installed package (osa/data/, put there at build time) or, in a source checkout, from the repo.
"""
from __future__ import annotations

import json
import re
from functools import cache, lru_cache
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

_HERE = Path(__file__).resolve().parent
SCHEMA_NAMES = ("envelope", "subscription", "audit", "stream", "metrics", "alert")


def _paths() -> dict[str, Path]:
    data = _HERE / "data"
    if (data / "SPEC.md").is_file():
        return {"spec": data / "SPEC.md", "schemas": data / "schemas", "fixtures": data / "fixtures"}
    root = _HERE.parent
    return {"spec": root / "spec" / "SPEC.md", "schemas": root / "schemas", "fixtures": root / "conformance" / "fixtures"}


@lru_cache(maxsize=1)
def spec_text() -> str:
    return _paths()["spec"].read_text(encoding="utf-8")


_HEADING = re.compile(r"^(#{2,3}) (.+?)\s*$")


@lru_cache(maxsize=1)
def sections() -> list[dict]:
    """Every ## and ### heading with its id ("6.3", "A.1"), title, level and text."""
    lines = spec_text().splitlines()
    heads = []
    for i, line in enumerate(lines):
        m = _HEADING.match(line)
        if m:
            title = m.group(2)
            ident = re.match(r"^(?:Appendix\s+)?([0-9A-Z]+(?:\.[0-9]+)*)\.?\s", title)
            heads.append((i, len(m.group(1)), ident.group(1) if ident else title, title))
    out = []
    for n, (i, level, ident, title) in enumerate(heads):
        end = next((j for j, lv, _, _ in heads[n + 1:] if lv <= level), len(lines))
        out.append({"id": ident, "title": title, "level": level, "text": "\n".join(lines[i:end]).strip()})
    return out


def get_section(ref: str) -> dict:
    """Find a section by id ("6.3", "§6.3", "A.1") or by a word from its title ("dedupe")."""
    ref = ref.strip().lstrip("§").strip()
    secs = sections()
    for s in secs:
        if s["id"].lower() == ref.lower().rstrip("."):
            return s
    hits = [s for s in secs if ref.lower() in s["title"].lower()]
    if not hits:
        raise KeyError(f"no section matches {ref!r}; use osa_list_sections to see them")
    return hits[0]


def search(query: str, limit: int = 20) -> list[dict]:
    q = query.strip().lower()
    if not q:
        raise ValueError("query is empty")
    by_title = {s["title"]: s for s in sections()}
    hits, current = [], None
    for line in spec_text().splitlines():
        m = _HEADING.match(line)
        if m:
            current = by_title.get(m.group(2))
        if q in line.lower():
            hits.append({"section": current["id"] if current else None,
                         "title": current["title"] if current else None, "line": line.strip()})
            if len(hits) >= limit:
                break
    return hits


@cache
def schema(name: str) -> dict:
    if name not in SCHEMA_NAMES:
        raise KeyError(f"unknown schema {name!r}; one of {', '.join(SCHEMA_NAMES)}")
    return json.loads((_paths()["schemas"] / f"{name}.schema.json").read_text(encoding="utf-8"))


@cache
def _registry() -> Registry:
    """Every bundled schema under its $id, so cross-schema $refs resolve locally, never over the network."""
    return Registry().with_resources(
        (schema(n)["$id"], Resource.from_contents(schema(n))) for n in SCHEMA_NAMES)


def validate(kind: str, document) -> dict:
    """Validate a document against one of the OSA schemas. Returns every error, not just the first."""
    v = Draft202012Validator(schema(kind), registry=_registry())
    errors = [{"path": "/" + "/".join(str(p) for p in e.absolute_path), "message": e.message}
              for e in sorted(v.iter_errors(document), key=lambda e: list(map(str, e.absolute_path)))]
    return {"kind": kind, "valid": not errors, "errors": errors}


def fixtures() -> list[dict]:
    out = []
    for f in sorted(_paths()["fixtures"].glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        out.append({"name": f.stem, "description": d.get("description", ""),
                    "subscriptions": len(d.get("subscriptions", [])), "cases": len(d.get("cases", []))})
    return out


def fixture(name: str) -> dict:
    p = _paths()["fixtures"] / f"{name}.json"
    if not p.is_file():
        raise KeyError(f"unknown fixture {name!r}; one of {', '.join(f['name'] for f in fixtures())}")
    return json.loads(p.read_text(encoding="utf-8"))
