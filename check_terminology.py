#!/usr/bin/env python3
"""Check terminology.yaml against the rules in README.md ("Terminology").

Run from the repo root: python3 check_terminology.py (needs PyYAML). Exits 1 on
any error. The same script runs in CI on every push and pull request.

`python3 check_terminology.py <file>` checks another copy of the file, which is
how a repo that syncs the terminology can check what it fetched.
"""
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
GROUPS = ["Products", "Models", "Evaluation", "Model Marketplace"]
STATUSES = {"current", "proposed"}
REQUIRED = {"id", "term", "group", "status", "definition"}
OPTIONAL = {"note", "details", "aliases", "avoid", "see_also"}
ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def is_text(value) -> bool:
    return isinstance(value, str) and value.strip() != ""


def name_key(name: str) -> str:
    """A name as lower-case words, so 'chap-core', 'chap_core' and 'Chap core' are one name."""
    return " ".join(re.sub(r"[-_/]+", " ", name.lower()).split())


def check_terms(terms) -> list:
    """The errors in a parsed terminology file, as text. An empty list means it is valid."""
    if not isinstance(terms, list) or not terms:
        return ["must be a non-empty list of terms"]
    errors: list = []
    ids: set = set()
    names: dict = {}  # name key -> id of the term that has it
    for i, entry in enumerate(terms):
        if not isinstance(entry, dict):
            errors.append(f"term #{i + 1}: is not a mapping")
            continue
        term_id = entry.get("id")
        where = term_id if isinstance(term_id, str) and term_id else f"term #{i + 1}"
        keys = set(entry)
        for key in sorted(REQUIRED - keys):
            errors.append(f"{where}: missing `{key}`")
        for key in sorted(keys - REQUIRED - OPTIONAL):
            errors.append(f"{where}: unknown field `{key}`")

        if term_id is not None:
            if not (isinstance(term_id, str) and ID_RE.match(term_id)):
                errors.append(f"{where}: `id` must be kebab-case, got {term_id!r}")
            elif term_id in ids:
                errors.append(f"{where}: duplicate id")
            else:
                ids.add(term_id)

        for key in ("term", "definition", "note", "details"):
            if key in entry and not is_text(entry[key]):
                errors.append(f"{where}: `{key}` must be non-empty text")
        if "group" in entry and entry["group"] not in GROUPS:
            errors.append(f"{where}: `group` must be one of {GROUPS}, got {entry['group']!r}")
        if "status" in entry and entry["status"] not in STATUSES:
            errors.append(f"{where}: `status` must be one of {sorted(STATUSES)}, got {entry['status']!r}")

        entry_names = [entry["term"]] if is_text(entry.get("term")) else []
        for key in ("aliases", "avoid"):
            value = entry.get(key)
            if value is None:
                continue
            if not isinstance(value, list) or not value or not all(is_text(x) for x in value):
                errors.append(f"{where}: `{key}` must be a non-empty list of names")
            else:
                entry_names += value
        # One name leads to one term, so a lookup has one answer.
        # A term may list a spelling of its own name ("CHAP" under Chap), but not the same one twice.
        if len(set(entry_names)) != len(entry_names):
            errors.append(f"{where}: a name is listed twice in `term`, `aliases` and `avoid`")
        for key in {name_key(name) for name in entry_names}:
            if key in names:
                errors.append(f"{where}: the name {key!r} is already a name of `{names[key]}`")
            else:
                names[key] = where

    for entry in terms:
        if not isinstance(entry, dict) or "see_also" not in entry:
            continue
        where = entry.get("id") or "?"
        see_also = entry["see_also"]
        if not isinstance(see_also, list) or not see_also or not all(isinstance(x, str) for x in see_also):
            errors.append(f"{where}: `see_also` must be a non-empty list of term ids")
            continue
        for other in see_also:
            if other == entry.get("id"):
                errors.append(f"{where}: `see_also` points to the term itself")
            elif other not in ids:
                errors.append(f"{where}: `see_also` names `{other}`, which is not a term id")
        if len(set(see_also)) != len(see_also):
            errors.append(f"{where}: `see_also` lists a term twice")
    return errors


def main(argv: list) -> int:
    path = Path(argv[1]) if len(argv) > 1 else ROOT / "terminology.yaml"
    if not path.exists():
        print(f"error: {path}: file missing")
        return 1
    try:
        terms = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        print(f"error: {path.name}: not valid YAML: {error}")
        return 1
    errors = check_terms(terms)
    for error in errors:
        print(f"error: {path.name}: {error}")
    count = len(terms) if isinstance(terms, list) else 0
    print(f"{count} terms checked, {len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
