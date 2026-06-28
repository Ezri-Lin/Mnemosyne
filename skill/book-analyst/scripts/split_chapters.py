#!/usr/bin/env python3
"""Split extracted text into chapter text files and an index."""

import argparse
import json
import re
from pathlib import Path


EN_HEADING = re.compile(r"^\s*chapter\s+([0-9]+|[IVXLCDM]+)\s*[:.\-–—]?\s*(.*?)\s*$", re.IGNORECASE)
ZH_HEADING = re.compile(r"^\s*第\s*([一二三四五六七八九十百零〇0-9]+)\s*[章节回]\s*(.*?)\s*$")


def roman_to_int(value):
    mapping = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    total = 0
    prev = 0
    for char in reversed(value.upper()):
        current = mapping.get(char, 0)
        if current < prev:
            total -= current
        else:
            total += current
            prev = current
    return total or None


def heading_for(line, fallback_number):
    match = EN_HEADING.match(line)
    if match:
        raw = match.group(1)
        number = int(raw) if raw.isdigit() else roman_to_int(raw) or fallback_number
        title = match.group(2).strip() or f"Chapter {number}"
        return number, title
    match = ZH_HEADING.match(line)
    if match:
        raw = match.group(1)
        number = int(raw) if raw.isdigit() else fallback_number
        title = match.group(2).strip() or f"第{raw}章"
        return number, title
    return None


def detect_headings(lines):
    headings = []
    for idx, line in enumerate(lines):
        found = heading_for(line, len(headings) + 1)
        if found:
            number, title = found
            headings.append({"line": idx, "number": number, "title": title})
    return headings


def split_chapters(text_path, output_dir):
    text_path = Path(text_path).expanduser().resolve()
    output_dir = Path(output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    text = text_path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    headings = detect_headings(lines)
    if not headings:
        headings = [{"line": 0, "number": 1, "title": text_path.stem}]

    chapters = []
    for order, heading in enumerate(headings, start=1):
        start = heading["line"]
        end = headings[order]["line"] if order < len(headings) else len(lines)
        chapter_id = f"ch{order:02d}"
        filename = f"{chapter_id}.txt"
        chapter_text = "\n".join(lines[start:end]).strip() + "\n"
        (output_dir / filename).write_text(chapter_text, encoding="utf-8")
        chapters.append({
            "id": chapter_id,
            "number": heading["number"],
            "title": heading["title"],
            "sourceFile": filename,
            "startLine": start + 1,
            "endLine": end,
            "sourceRange": f"lines {start + 1}-{end}",
            "charCount": len(chapter_text),
        })

    index = {"sourceText": str(text_path), "chapters": chapters}
    (output_dir / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return index


def main():
    parser = argparse.ArgumentParser(description="Split extracted text into chapter files.")
    parser.add_argument("text_path")
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    result = split_chapters(args.text_path, args.output_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
