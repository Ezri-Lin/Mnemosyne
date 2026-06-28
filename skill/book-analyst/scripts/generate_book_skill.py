#!/usr/bin/env python3
"""Generate a small knowledge skill from a book's analyzed knowledge."""

import argparse
import json
import re
from pathlib import Path


def slugify(value):
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", value)
    return value.strip("-") or "book"


def load_json(path, fallback):
    path = Path(path)
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def concept_name(concept):
    return concept.get("name") or concept.get("title") or concept.get("id") or "Unnamed concept"


def generate_book_skill(analysis_dir, output_root):
    analysis_dir = Path(analysis_dir).expanduser().resolve()
    output_root = Path(output_root).expanduser().resolve()
    book = load_json(analysis_dir / "book.json", {})
    concepts = load_json(analysis_dir / "concepts" / "index.json", {"concepts": []})
    evidence = load_json(analysis_dir / "evidence" / "index.json", {"evidence": []})

    book_id = book.get("id") or slugify(book.get("title") or analysis_dir.name)
    skill_name = f"{slugify(book_id)}-knowledge"
    skill_dir = output_root / skill_name
    refs = skill_dir / "references"
    agents = skill_dir / "agents"
    refs.mkdir(parents=True, exist_ok=True)
    agents.mkdir(parents=True, exist_ok=True)

    title = book.get("title") or book_id
    description = (
        f"Use when reasoning with concepts, frameworks, and evidence extracted from {title}. "
        "Supports deep thinking, reading recall, and applying the book's knowledge without rereading the whole source."
    )
    skill_md = f"""---
name: {skill_name}
description: "{description}"
---

# {title} Knowledge

Use this skill when the user wants to think with ideas from **{title}**.

Read `references/knowledge.md` for the extracted concepts, thesis, and evidence map.

Rules:

- Treat this as a thinking aid, not as the original book.
- Do not invent quotes or claims.
- When a claim needs source backing, point to the evidence ids and source ranges in `knowledge.md`.
- If the user asks for personal application, separate book evidence from interpretation.
"""
    (skill_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")

    lines = [
        f"# {title}",
        "",
        f"Author: {book.get('author', '')}",
        "",
        "## Thesis",
        "",
        book.get("thesis", ""),
        "",
        "## Core Question",
        "",
        book.get("coreQuestion", ""),
        "",
        "## Concepts",
        "",
    ]
    for concept in concepts.get("concepts", []):
        lines.append(f"### {concept_name(concept)}")
        lines.append("")
        lines.append(concept.get("definition") or concept.get("oneLine") or "")
        if concept.get("chapterIds"):
            lines.append("")
            lines.append("Chapters: " + ", ".join(concept.get("chapterIds", [])))
        lines.append("")
    lines.extend(["## Evidence", ""])
    for item in evidence.get("evidence", []):
        lines.append(f"### {item.get('id', '')} · {item.get('title', '')}")
        lines.append("")
        lines.append(f"Type: {item.get('type', '')}")
        lines.append(f"Source: {item.get('sourceRange', '')}")
        lines.append("")
        lines.append(item.get("summary", ""))
        if item.get("aiUnderstanding"):
            lines.append("")
            lines.append("AI understanding: " + item.get("aiUnderstanding", ""))
        lines.append("")
    (refs / "knowledge.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    openai_yaml = f"""interface:
  display_name: "{title} Knowledge"
  short_description: "Think with this book's core ideas"
  default_prompt: "Use ${skill_name} to help me reason with ideas from {title}."

policy:
  allow_implicit_invocation: true
"""
    (agents / "openai.yaml").write_text(openai_yaml, encoding="utf-8")
    return skill_dir


def main():
    parser = argparse.ArgumentParser(description="Generate a reusable knowledge skill from analyzed book data.")
    parser.add_argument("analysis_dir")
    parser.add_argument("--output-root", default="generated-skills")
    args = parser.parse_args()
    path = generate_book_skill(args.analysis_dir, args.output_root)
    print(path)


if __name__ == "__main__":
    main()
