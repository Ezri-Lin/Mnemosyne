#!/usr/bin/env python3
"""Render fixed Book Analyst templates from analysis JSON."""

import argparse
import json
from pathlib import Path
from urllib.parse import quote


LOGO_SVG = """<svg class="mnemo-mark" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" role="img" aria-labelledby="mnemo-logo-title mnemo-logo-desc" color="currentColor"><title id="mnemo-logo-title">Mnemosyne Codex Seal</title><desc id="mnemo-logo-desc">A double-ring codex seal with an open book and muse star.</desc><circle cx="50" cy="50" r="45" fill="none" stroke="currentColor" stroke-width="3"/><circle cx="50" cy="50" r="39.5" fill="none" stroke="currentColor" stroke-width="1.3"/><g fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><path d="M50 50 C43 46 33 45 26 47 L26 67 C33 65 43 66 50 70" stroke-width="2.8"/><path d="M50 50 C57 46 67 45 74 47 L74 67 C67 65 57 66 50 70" stroke-width="2.8"/><line x1="50" y1="50" x2="50" y2="70" stroke-width="2.8"/><path d="M45 52 C39 49 33 49 29 50" stroke-width="1.1"/><path d="M55 52 C61 49 67 49 71 50" stroke-width="1.1"/><path d="M45 56 C39 53 33 53 29 54" stroke-width="1.1"/><path d="M55 56 C61 53 67 53 71 54" stroke-width="1.1"/></g><path d="M50 22 L52 28.5 L58.5 30.5 L52 32.5 L50 39 L48 32.5 L41.5 30.5 L48 28.5 Z" fill="currentColor"/></svg>"""
FAVICON_DATA_URI = "data:image/svg+xml," + quote(LOGO_SVG.replace('class="mnemo-mark" ', ""), safe="")


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


def brand_values():
    return {
        "{{LOGO_SVG}}": LOGO_SVG,
        "{{FAVICON_DATA_URI}}": FAVICON_DATA_URI,
    }


def render_library(config_path, books):
    config = read_config(config_path)
    templates = Path(config["installedAssets"]["pageTemplates"])
    web_root = Path(config["webOutputRoot"])
    web_root.mkdir(parents=True, exist_ok=True)
    template = (templates / "library-empty.html").read_text(encoding="utf-8")
    output = replace_many(template, {**brand_values(), "{{BOOKS_JSON}}": json_for_script(books)})
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
        **brand_values(),
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
            **brand_values(),
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
