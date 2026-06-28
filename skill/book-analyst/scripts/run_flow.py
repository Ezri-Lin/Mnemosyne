#!/usr/bin/env python3
"""Run the deterministic part of the Book Analyst flow."""

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from init_project import initialize_project
from prepare_book import prepare_book
from render_project import render_book


def ensure_config(project_root):
    project_root = Path(project_root).expanduser().resolve()
    config_path = project_root / ".book-analyst" / "config.json"
    if not config_path.exists():
        initialize_project(project_root)
    return config_path


def main():
    parser = argparse.ArgumentParser(description="Initialize project and prepare a book for AI analysis.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--source", help="Book source path. If omitted, only initialization runs.")
    parser.add_argument("--book-id", default=None)
    parser.add_argument("--title", default=None)
    parser.add_argument("--author", default=None)
    parser.add_argument("--language", default=None)
    parser.add_argument("--render", action="store_true", help="Render HTML after analysis JSON has been filled.")
    args = parser.parse_args()

    config_path = ensure_config(args.project_root)
    result = {"config": str(config_path)}
    if args.source:
        manifest = prepare_book(config_path, args.source, title=args.title, author=args.author, language=args.language, book_id=args.book_id)
        result["preparedBook"] = manifest
        result["aiNextStep"] = [
            "Fill analysis/<book-id>/book.json",
            "Fill analysis/<book-id>/themes.json",
            "Fill analysis/<book-id>/evidence/index.json",
            "Fill analysis/<book-id>/concepts/index.json",
            "Select must-read chapters and fill analysis/<book-id>/chapters/chXX.json",
        ]
        book_id = manifest["bookId"]
        if args.render:
            outputs = render_book(config_path, book_id)
            result["rendered"] = {
                "note": "Rendered with current JSON. If JSON is still empty, pages show empty states.",
                "outputs": {
                    "bookHome": str(outputs["bookHome"]),
                    "chapters": [str(path) for path in outputs["chapters"]],
                },
            }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
