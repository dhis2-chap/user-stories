#!/usr/bin/env python3
"""Check the story files against the rules in README.md.

Run from the repo root: python3 check_stories.py (needs PyYAML). Exits 1 on any
error. The same script runs in CI on every push and pull request.
"""
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
STORY_FILES = ["modeling.yaml", "modeling-app.yaml", "climate-data.yaml", "cross-domain.yaml"]
STATUSES = {"current", "planned", "proposed"}
REQUIRED = {"id", "reader", "goal", "status"}
OPTIONAL = {"starts_at", "done_when", "jira", "notes", "why", "context"}
ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
JIRA_RE = re.compile(r"^[A-Z][A-Z0-9]+-\d+$")
# A sentence end inside the goal: terminator, space, capital letter. "e.g. nightly" passes.
SENTENCE_BREAK_RE = re.compile(r"[.!?]\s+[A-Z]")


def is_text(value) -> bool:
    return isinstance(value, str) and value.strip() != ""


def check_story(story, where: str, errors: list) -> None:
    if not isinstance(story, dict):
        errors.append(f"{where}: story is not a mapping")
        return
    keys = set(story)
    for key in sorted(REQUIRED - keys):
        errors.append(f"{where}: missing `{key}`")
    for key in sorted(keys - REQUIRED - OPTIONAL):
        errors.append(f"{where}: unknown field `{key}`")

    story_id = story.get("id")
    if story_id is not None and not (isinstance(story_id, str) and ID_RE.match(story_id)):
        errors.append(f"{where}: `id` must be kebab-case, got {story_id!r}")

    for key in ("reader", "goal", "why", "context", "notes"):
        if key in story and not is_text(story[key]):
            errors.append(f"{where}: `{key}` must be non-empty text")

    goal = story.get("goal")
    if is_text(goal) and SENTENCE_BREAK_RE.search(goal.strip()):
        errors.append(f"{where}: `goal` must be one sentence")

    status = story.get("status")
    if status not in STATUSES:
        errors.append(f"{where}: `status` must be one of {sorted(STATUSES)}, got {status!r}")

    starts_at = story.get("starts_at")
    if starts_at is not None:
        if not isinstance(starts_at, list):
            errors.append(f"{where}: `starts_at` must be a list")
        else:
            for i, entry in enumerate(starts_at):
                if not isinstance(entry, dict) or set(entry) != {"repo", "path"}:
                    errors.append(f"{where}: `starts_at[{i}]` must have exactly `repo` and `path`")
                    continue
                if not (is_text(entry["repo"]) and REPO_RE.match(entry["repo"])):
                    errors.append(f"{where}: `starts_at[{i}].repo` must be org/name on GitHub")
                if not is_text(entry["path"]):
                    errors.append(f"{where}: `starts_at[{i}].path` must be non-empty text")
    if status == "current" and not starts_at:
        errors.append(f"{where}: a `current` story needs a non-empty `starts_at`")

    if status == "proposed" and not is_text(story.get("notes")):
        errors.append(f"{where}: a `proposed` story needs `notes` saying who asked for it and why")

    done_when = story.get("done_when")
    if done_when is not None:
        if not isinstance(done_when, list) or not done_when or not all(is_text(x) for x in done_when):
            errors.append(f"{where}: `done_when` must be a non-empty list of text items")

    jira = story.get("jira")
    if jira is not None:
        if not isinstance(jira, list) or not all(isinstance(x, str) and JIRA_RE.match(x) for x in jira):
            errors.append(f"{where}: `jira` must be a list of issue keys such as CLIM-374")


def check_readers(errors: list) -> set:
    path = ROOT / "readers.yaml"
    if not path.exists():
        return set()
    data = yaml.safe_load(path.read_text())
    if not isinstance(data, list):
        errors.append("readers.yaml: must be a list of readers")
        return set()
    keys = set()
    for i, reader in enumerate(data):
        where = f"readers.yaml[{i}]"
        if not isinstance(reader, dict) or not is_text(reader.get("key")):
            errors.append(f"{where}: needs a `key`")
            continue
        if not ID_RE.match(reader["key"]):
            errors.append(f"{where}: `key` must be kebab-case")
        if reader["key"] in keys:
            errors.append(f"{where}: duplicate key `{reader['key']}`")
        keys.add(reader["key"])
        for key in ("name", "description"):
            if not is_text(reader.get(key)):
                errors.append(f"{where} ({reader['key']}): needs `{key}`")
    return keys


def main() -> int:
    errors: list = []
    ids: dict = {}
    readers_used: dict = {}
    current_without_done_when: list = []
    for name in STORY_FILES:
        path = ROOT / name
        if not path.exists():
            errors.append(f"{name}: file missing")
            continue
        stories = yaml.safe_load(path.read_text())
        if not isinstance(stories, list):
            errors.append(f"{name}: must be a list of stories")
            continue
        for i, story in enumerate(stories):
            story_id = story.get("id") if isinstance(story, dict) else None
            where = f"{name}: {story_id or f'story #{i + 1}'}"
            check_story(story, where, errors)
            if isinstance(story_id, str):
                if story_id in ids:
                    errors.append(f"{where}: duplicate id, also in {ids[story_id]}")
                ids[story_id] = name
                if is_text(story.get("reader")):
                    readers_used.setdefault(story["reader"], []).append(story_id)
                if story.get("status") == "current" and "done_when" not in story:
                    current_without_done_when.append(story_id)

    reader_keys = check_readers(errors)

    for error in errors:
        print(f"error: {error}")
    unknown = sorted(r for r in readers_used if r not in reader_keys)
    if reader_keys and unknown:
        print("note: reader names not in readers.yaml (not an error until the team agrees the list):")
        for reader in unknown:
            print(f"  - {reader!r}: {', '.join(readers_used[reader])}")
    if current_without_done_when:
        print("note: `current` stories without `done_when` (not an error yet; the goal is the only test):")
        for story_id in current_without_done_when:
            print(f"  - {story_id}")
    print(f"{len(ids)} stories checked, {len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
