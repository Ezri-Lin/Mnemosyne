#!/usr/bin/env python3
"""Validate a project initialized for the book-analyst skill."""

import argparse
import json
import sys
from pathlib import Path


REQUIRED_CONFIG_FIELDS = [
    "projectRoot",
    "bookSourceRoot",
    "analysisOutputRoot",
    "webOutputRoot",
    "notesOutputRoot",
    "knowledgeOutputRoot",
    "metadataStore",
    "language",
    "theme",
    "density",
    "installedAssets",
]

REQUIRED_PAGE_TEMPLATES = [
    "library-empty.html",
    "book-home-empty.html",
    "chapter-page-empty.html",
]

REQUIRED_SKELETONS = [
    "manifest.empty.json",
    "analysis/book.empty.json",
    "analysis/themes.empty.json",
    "analysis/concepts/index.empty.json",
    "analysis/chapters/index.empty.json",
    "analysis/chapters/chapter.empty.json",
    "analysis/evidence/index.empty.json",
]


def fail(errors, message):
    errors.append(message)


def load_json(path, errors):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(errors, f"Invalid JSON: {path} ({exc})")
        return None


def main():
    parser = argparse.ArgumentParser(description="Validate Book Analyst project config and installed assets.")
    parser.add_argument("--config", default=".book-analyst/config.json")
    args = parser.parse_args()

    config_path = Path(args.config).expanduser().resolve()
    errors = []
    if not config_path.exists():
        print(f"Missing config: {config_path}", file=sys.stderr)
        return 1

    config = load_json(config_path, errors) or {}
    for field in REQUIRED_CONFIG_FIELDS:
        if field not in config:
            fail(errors, f"Missing config field: {field}")

    for field in ["projectRoot", "bookSourceRoot", "analysisOutputRoot", "webOutputRoot", "notesOutputRoot", "knowledgeOutputRoot"]:
        value = config.get(field)
        if value and not Path(value).exists():
            fail(errors, f"Configured path does not exist: {field}={value}")

    installed = config.get("installedAssets") or {}
    page_templates = Path(installed.get("pageTemplates", ""))
    data_skeletons = Path(installed.get("dataSkeletons", ""))

    for name in REQUIRED_PAGE_TEMPLATES:
        path = page_templates / name
        if not path.exists():
            fail(errors, f"Missing page template: {path}")

    for name in REQUIRED_SKELETONS:
        path = data_skeletons / name
        if not path.exists():
            fail(errors, f"Missing data skeleton: {path}")
        else:
            load_json(path, errors)

    if errors:
        print("Book Analyst validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Book Analyst validation ok: {config_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
