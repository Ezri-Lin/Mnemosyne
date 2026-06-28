#!/usr/bin/env python3
"""Prepare a source book: copy/extract text, split chapters, and create per-book folders."""

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from extract_book import extract_book
from split_chapters import split_chapters


def slugify(value):
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", value)
    return value.strip("-") or "book"


def load_json(path):
    return json.loads(Path(path).expanduser().resolve().read_text(encoding="utf-8"))


def copy_skeletons(config, book_id):
    data_skeletons = Path(config["installedAssets"]["dataSkeletons"])
    analysis_root = Path(config["analysisOutputRoot"]) / book_id
    (analysis_root / "chapters").mkdir(parents=True, exist_ok=True)
    (analysis_root / "evidence").mkdir(parents=True, exist_ok=True)
    (analysis_root / "concepts").mkdir(parents=True, exist_ok=True)
    targets = {
        data_skeletons / "analysis" / "book.empty.json": analysis_root / "book.json",
        data_skeletons / "analysis" / "themes.empty.json": analysis_root / "themes.json",
        data_skeletons / "analysis" / "chapters" / "index.empty.json": analysis_root / "chapters" / "index.json",
        data_skeletons / "analysis" / "chapters" / "chapter.empty.json": analysis_root / "chapters" / "chapter.empty.json",
        data_skeletons / "analysis" / "evidence" / "index.empty.json": analysis_root / "evidence" / "index.json",
        data_skeletons / "analysis" / "concepts" / "index.empty.json": analysis_root / "concepts" / "index.json",
    }
    for src, dest in targets.items():
        if not dest.exists():
            shutil.copy2(src, dest)
    return analysis_root


def prepare_book(config_path, source_path, title=None, author=None, language=None, book_id=None):
    config = load_json(config_path)
    title_guess = title or Path(source_path).stem
    book_id = book_id or slugify(title_guess)
    source_root = Path(config["bookSourceRoot"]) / book_id
    source_root.mkdir(parents=True, exist_ok=True)
    metadata = extract_book(source_path, source_root, title=title, author=author, language=language or config.get("language"))
    metadata["bookId"] = book_id

    analysis_root = copy_skeletons(config, book_id)
    split_result = split_chapters(source_root / "extracted.txt", analysis_root / "source-chapters")

    manifest = {
        "bookId": book_id,
        "metadata": metadata,
        "sourceChapters": split_result,
        "nextStep": "Ask the AI Agent to fill analysis/book.json, themes.json, evidence/index.json, and high-value chapter JSON files."
    }
    (analysis_root / "import-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def main():
    parser = argparse.ArgumentParser(description="Prepare a book for AI analysis.")
    parser.add_argument("source")
    parser.add_argument("--config", default=".book-analyst/config.json")
    parser.add_argument("--book-id", default=None)
    parser.add_argument("--title", default=None)
    parser.add_argument("--author", default=None)
    parser.add_argument("--language", default=None)
    args = parser.parse_args()
    result = prepare_book(args.config, args.source, title=args.title, author=args.author, language=args.language, book_id=args.book_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
