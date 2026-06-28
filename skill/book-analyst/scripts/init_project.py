#!/usr/bin/env python3
"""Initialize a project for the book-analyst skill."""

import argparse
import json
import shutil
from pathlib import Path
from datetime import datetime


def ask(label, default):
    value = input(f"{label} [{default}]: ").strip()
    return value or default


def resolve(base, value):
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = base / path
    return path.resolve()


def copytree(src, dest):
    shutil.copytree(src, dest, dirs_exist_ok=True)


def initialize_project(
    project_root,
    books_dir=None,
    analysis_dir=None,
    web_dir=None,
    notes_dir=None,
    knowledge_dir=None,
    metadata_store=None,
    language="zh-CN",
    theme="warm-paper",
    density="balanced",
    non_interactive=False,
):
    project_root = Path(project_root).expanduser().resolve()
    project_root.mkdir(parents=True, exist_ok=True)

    def choose(name, arg_value, default):
        if arg_value:
            return arg_value
        if non_interactive:
            return default
        return ask(name, default)

    books_dir = resolve(project_root, choose("Book source directory", books_dir, "source"))
    analysis_dir = resolve(project_root, choose("Analysis output directory", analysis_dir, "analysis"))
    web_dir = resolve(project_root, choose("Web output directory", web_dir, "web"))
    notes_dir = resolve(project_root, choose("Notes output directory", notes_dir, "notes"))
    knowledge_dir = resolve(project_root, choose("Knowledge output directory", knowledge_dir, "knowledge"))
    metadata_store = choose("Metadata store", metadata_store, str(project_root / "mnemosyne.db"))

    for directory in [books_dir, analysis_dir, web_dir, notes_dir, knowledge_dir]:
        directory.mkdir(parents=True, exist_ok=True)

    skill_root = Path(__file__).resolve().parents[1]
    install_root = project_root / ".book-analyst"
    install_root.mkdir(parents=True, exist_ok=True)
    copytree(skill_root / "assets" / "page-templates", install_root / "page-templates")
    copytree(skill_root / "assets" / "data-skeletons", install_root / "data-skeletons")

    config = {
        "schemaVersion": "book-analyst-config-v1",
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "projectRoot": str(project_root),
        "bookSourceRoot": str(books_dir),
        "analysisOutputRoot": str(analysis_dir),
        "webOutputRoot": str(web_dir),
        "notesOutputRoot": str(notes_dir),
        "knowledgeOutputRoot": str(knowledge_dir),
        "metadataStore": metadata_store,
        "language": language,
        "theme": theme,
        "density": density,
        "installedAssets": {
            "pageTemplates": str(install_root / "page-templates"),
            "dataSkeletons": str(install_root / "data-skeletons")
        }
    }

    config_path = install_root / "config.json"
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Book Analyst project initialized: {config_path}")
    print(f"Installed page templates: {install_root / 'page-templates'}")
    print(f"Installed data skeletons: {install_root / 'data-skeletons'}")
    return config


def main():
    parser = argparse.ArgumentParser(description="Install Book Analyst config, empty page templates, and data skeletons.")
    parser.add_argument("--project-root", default=".", help="Project or vault root.")
    parser.add_argument("--books-dir", default=None, help="Directory that stores source books.")
    parser.add_argument("--analysis-dir", default=None, help="Directory for generated analysis JSON.")
    parser.add_argument("--web-dir", default=None, help="Directory for generated HTML.")
    parser.add_argument("--notes-dir", default=None, help="Directory for generated Markdown notes.")
    parser.add_argument("--knowledge-dir", default=None, help="Directory for permanent note candidates or knowledge output.")
    parser.add_argument("--metadata-store", default=None, help="SQLite path, JSON path, or external metadata store id.")
    parser.add_argument("--language", default="zh-CN")
    parser.add_argument("--theme", default="warm-paper")
    parser.add_argument("--density", default="balanced")
    parser.add_argument("--non-interactive", action="store_true")
    args = parser.parse_args()
    initialize_project(
        args.project_root,
        books_dir=args.books_dir,
        analysis_dir=args.analysis_dir,
        web_dir=args.web_dir,
        notes_dir=args.notes_dir,
        knowledge_dir=args.knowledge_dir,
        metadata_store=args.metadata_store,
        language=args.language,
        theme=args.theme,
        density=args.density,
        non_interactive=args.non_interactive,
    )


if __name__ == "__main__":
    main()
