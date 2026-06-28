#!/usr/bin/env python3
"""Extract a source book into original file, extracted.txt, and metadata.json."""

import argparse
import json
import re
import shutil
from datetime import datetime
from pathlib import Path


SUPPORTED = {".txt", ".md", ".markdown", ".html", ".htm", ".epub", ".pdf"}


def title_from_path(path):
    return path.stem.replace("_", " ").replace("-", " ").strip()


def read_text_file(path):
    return path.read_text(encoding="utf-8", errors="replace")


def read_html(path):
    html = path.read_text(encoding="utf-8", errors="replace")
    try:
        from bs4 import BeautifulSoup
        return BeautifulSoup(html, "html.parser").get_text("\n")
    except Exception:
        return re.sub(r"<[^>]+>", " ", html)


def read_epub(path):
    try:
        from ebooklib import epub
        from ebooklib import ITEM_DOCUMENT
        from bs4 import BeautifulSoup
    except Exception as exc:
        raise RuntimeError("EPUB extraction requires ebooklib and beautifulsoup4") from exc
    book = epub.read_epub(str(path))
    chunks = []
    for item in book.get_items():
        if item.get_type() == ITEM_DOCUMENT:
            soup = BeautifulSoup(item.get_content(), "html.parser")
            text = soup.get_text("\n").strip()
            if text:
                chunks.append(text)
    return "\n\n".join(chunks)


def read_pdf(path):
    try:
        from PyPDF2 import PdfReader
    except Exception as exc:
        raise RuntimeError("PDF extraction requires PyPDF2") from exc
    reader = PdfReader(str(path))
    chunks = []
    for page in reader.pages:
        text = page.extract_text() or ""
        if text.strip():
            chunks.append(text.strip())
    return "\n\n".join(chunks)


def extract_text(path):
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md", ".markdown"}:
        return read_text_file(path)
    if suffix in {".html", ".htm"}:
        return read_html(path)
    if suffix == ".epub":
        return read_epub(path)
    if suffix == ".pdf":
        return read_pdf(path)
    raise ValueError(f"Unsupported book format: {suffix}")


def count_words(text):
    return len(re.findall(r"[\w']+", text, flags=re.UNICODE))


def extract_book(source_path, output_dir, title=None, author=None, language=None):
    source_path = Path(source_path).expanduser().resolve()
    output_dir = Path(output_dir).expanduser().resolve()
    if source_path.suffix.lower() not in SUPPORTED:
        raise ValueError(f"Unsupported book format: {source_path.suffix}")
    output_dir.mkdir(parents=True, exist_ok=True)
    ext = source_path.suffix.lower().lstrip(".")
    original = output_dir / f"original.{ext}"
    shutil.copy2(source_path, original)
    text = extract_text(source_path)
    extracted = output_dir / "extracted.txt"
    extracted.write_text(text, encoding="utf-8")
    metadata = {
        "title": title or title_from_path(source_path),
        "author": author or "",
        "language": language or "",
        "sourceFormat": ext,
        "sourcePath": str(original),
        "extractedPath": str(extracted),
        "charCount": len(text),
        "wordCount": count_words(text),
        "extractedAt": datetime.now().isoformat(timespec="seconds"),
    }
    (output_dir / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return metadata


def main():
    parser = argparse.ArgumentParser(description="Extract a source book to text.")
    parser.add_argument("source")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--title", default=None)
    parser.add_argument("--author", default=None)
    parser.add_argument("--language", default=None)
    args = parser.parse_args()
    result = extract_book(args.source, args.output_dir, title=args.title, author=args.author, language=args.language)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
