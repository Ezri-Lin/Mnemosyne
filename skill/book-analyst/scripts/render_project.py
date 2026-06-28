#!/usr/bin/env python3
"""Render fixed Book Analyst templates from analysis JSON."""

import argparse
import json
from pathlib import Path


def load_json(path, fallback):
    path = Path(path)
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def json_for_script(value):
    return json.dumps(value, ensure_ascii=False).replace("</", "<\\/")


def read_config(config_path):
    return json.loads(Path(config_path).expanduser().resolve().read_text(encoding="utf-8"))


def replace_many(text, values):
    for key, value in values.items():
        text = text.replace(key, value)
    return text


def render_library(config_path, books):
    config = read_config(config_path)
    templates = Path(config["installedAssets"]["pageTemplates"])
    web_root = Path(config["webOutputRoot"])
    web_root.mkdir(parents=True, exist_ok=True)
    template = (templates / "library-empty.html").read_text(encoding="utf-8")
    output = replace_many(template, {"{{BOOKS_JSON}}": json_for_script(books)})
    path = web_root / "index.html"
    path.write_text(output, encoding="utf-8")
    return path


def chapter_json_path(chapter_root, chapter):
    candidates = [
        chapter_root / f"{chapter.get('id', '')}.json",
        chapter_root / f"ch{int(chapter.get('number', 0)):02d}.json" if chapter.get("number") else chapter_root / "_missing.json",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def render_book(config_path, book_id):
    config = read_config(config_path)
    templates = Path(config["installedAssets"]["pageTemplates"])
    analysis_root = Path(config["analysisOutputRoot"]) / book_id
    web_root = Path(config["webOutputRoot"]) / book_id
    web_root.mkdir(parents=True, exist_ok=True)
    (web_root / "chapters").mkdir(parents=True, exist_ok=True)

    book = load_json(analysis_root / "book.json", {})
    themes = load_json(analysis_root / "themes.json", {"themes": []})
    chapters = load_json(analysis_root / "chapters" / "index.json", {"chapters": []})
    evidence = load_json(analysis_root / "evidence" / "index.json", {"evidence": []})

    book_home = (templates / "book-home-empty.html").read_text(encoding="utf-8")
    book_home = replace_many(book_home, {
        "{{BOOK_JSON}}": json_for_script(book),
        "{{THEMES_JSON}}": json_for_script(themes),
        "{{CHAPTERS_JSON}}": json_for_script(chapters),
        "{{EVIDENCE_JSON}}": json_for_script(evidence),
        "{{LIBRARY_HREF}}": "../index.html",
    })
    book_home_path = web_root / "index.html"
    book_home_path.write_text(book_home, encoding="utf-8")

    chapter_template = (templates / "chapter-page-empty.html").read_text(encoding="utf-8")
    chapter_paths = []
    for chapter in chapters.get("chapters", []):
        detail = chapter.get("detailPage")
        if not detail:
            continue
        source = chapter_json_path(analysis_root / "chapters", chapter)
        chapter_data = load_json(source, {}) if source else {}
        rendered = replace_many(chapter_template, {
            "{{CHAPTER_JSON}}": json_for_script(chapter_data),
            "{{EVIDENCE_JSON}}": json_for_script(evidence),
            "{{LIBRARY_HREF}}": "../../index.html",
            "{{BOOK_HOME_HREF}}": "../index.html",
        })
        output_path = web_root / detail
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding="utf-8")
        chapter_paths.append(output_path)

    return {"bookHome": book_home_path, "chapters": chapter_paths}


def main():
    parser = argparse.ArgumentParser(description="Render Book Analyst HTML from analysis JSON.")
    parser.add_argument("--config", default=".book-analyst/config.json")
    parser.add_argument("--book-id", required=True)
    parser.add_argument("--library", action="store_true", help="Also render library index from books.json if present.")
    args = parser.parse_args()
    outputs = render_book(args.config, args.book_id)
    if args.library:
        config = read_config(args.config)
        books = load_json(Path(config["analysisOutputRoot"]) / "books.json", [])
        render_library(args.config, books)
    print(json.dumps({
        "bookHome": str(outputs["bookHome"]),
        "chapters": [str(p) for p in outputs["chapters"]],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
