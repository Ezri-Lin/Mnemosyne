import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skill" / "book-analyst" / "scripts"


def load_script(name):
    path = SCRIPTS / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class BookAnalystScriptTests(unittest.TestCase):
    def test_extract_book_writes_plain_text_and_metadata(self):
        extract_book = load_script("extract_book")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "Sample Book.md"
            source.write_text("# Sample Book\n\nChapter 1\nFirst idea.", encoding="utf-8")

            result = extract_book.extract_book(source, root / "source")

            self.assertEqual(result["title"], "Sample Book")
            self.assertEqual(result["sourceFormat"], "md")
            self.assertTrue((root / "source" / "original.md").exists())
            self.assertEqual((root / "source" / "extracted.txt").read_text(encoding="utf-8"), source.read_text(encoding="utf-8"))
            metadata = json.loads((root / "source" / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["wordCount"], 6)

    def test_split_chapters_detects_english_headings(self):
        split_chapters = load_script("split_chapters")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            text_path = root / "extracted.txt"
            text_path.write_text(
                "Preface\n\nChapter 1 The Door\nAlpha text.\n\nChapter 2 The Room\nBeta text.\n",
                encoding="utf-8",
            )

            result = split_chapters.split_chapters(text_path, root / "analysis" / "chapters")

            self.assertEqual(len(result["chapters"]), 2)
            self.assertEqual(result["chapters"][0]["title"], "The Door")
            self.assertEqual(result["chapters"][1]["id"], "ch02")
            self.assertTrue((root / "analysis" / "chapters" / "ch01.txt").exists())
            self.assertTrue((root / "analysis" / "chapters" / "index.json").exists())

    def test_render_book_outputs_book_home_and_chapter_pages(self):
        init_project = load_script("init_project")
        render_project = load_script("render_project")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_project.initialize_project(root, non_interactive=True)

            book_root = root / "analysis" / "demo-book"
            (book_root / "chapters").mkdir(parents=True)
            (book_root / "evidence").mkdir(parents=True)
            (book_root / "concepts").mkdir(parents=True)
            (book_root / "book.json").write_text(json.dumps({
                "id": "demo-book",
                "title": "Demo Book",
                "author": "Ada Reader",
                "language": "en",
                "thesis": "A test thesis.",
                "coreQuestion": "What does this book teach?",
                "readingRoute": "Read chapter one first.",
                "stats": {"chapterCount": 1, "mustReadCount": 1, "themeCount": 1, "evidenceCount": 1}
            }), encoding="utf-8")
            (book_root / "themes.json").write_text(json.dumps({"themes": [{
                "id": "theme-one",
                "title": "Theme One",
                "oneLine": "A theme.",
                "whyRead": "It matters.",
                "readingOrder": ["ch01"],
                "whatYouGet": "A map.",
                "chapterIds": ["ch01"],
                "conceptIds": [],
                "evidenceIds": ["ev1"]
            }]}), encoding="utf-8")
            (book_root / "chapters" / "index.json").write_text(json.dumps({"chapters": [{
                "id": "ch01",
                "number": 1,
                "originalTitle": "Opening",
                "readerTitle": "Opening Map",
                "roleInBook": "start",
                "valueDensity": 5,
                "recommendation": "must-read",
                "themeIds": ["theme-one"],
                "detailPage": "chapters/ch01-opening.html",
                "sourceRange": "Chapter 1"
            }]}), encoding="utf-8")
            (book_root / "chapters" / "ch01.json").write_text(json.dumps({
                "id": "ch01",
                "chapterNumber": 1,
                "originalTitle": "Opening",
                "readerTitle": "Opening Map",
                "oneLine": "The opening claim.",
                "roleCards": [{"label": "Role", "value": "Start", "body": "The entry point."}],
                "overviewCards": [{"title": "Claim", "body": "A compact claim.", "sourceRef": "ev1"}],
                "argumentChain": [],
                "frameworks": [],
                "cases": [],
                "research": [],
                "decisionRules": []
            }), encoding="utf-8")
            (book_root / "evidence" / "index.json").write_text(json.dumps({"evidence": [{
                "id": "ev1",
                "type": "quote",
                "title": "Opening Evidence",
                "sourceRange": "Chapter 1",
                "sourceHint": "Source hint.",
                "summary": "Evidence summary.",
                "whyImportant": "It supports the opening.",
                "aiUnderstanding": "AI explanation.",
                "readLocation": "Read the start.",
                "supports": ["ch01"]
            }]}), encoding="utf-8")

            outputs = render_project.render_book(root / ".book-analyst" / "config.json", "demo-book")

            self.assertTrue(outputs["bookHome"].exists())
            self.assertTrue(outputs["chapters"][0].exists())
            self.assertIn("Demo Book", outputs["bookHome"].read_text(encoding="utf-8"))
            self.assertNotIn("{{BOOK_JSON}}", outputs["bookHome"].read_text(encoding="utf-8"))

    def test_generate_book_skill_creates_skill_folder(self):
        generate_book_skill = load_script("generate_book_skill")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            analysis = root / "analysis" / "demo-book"
            (analysis / "concepts").mkdir(parents=True)
            (analysis / "book.json").write_text(json.dumps({
                "id": "demo-book",
                "title": "Demo Book",
                "author": "Ada Reader",
                "thesis": "A reusable idea.",
                "coreQuestion": "How should this guide thinking?"
            }), encoding="utf-8")
            (analysis / "concepts" / "index.json").write_text(json.dumps({
                "concepts": [{"id": "c1", "name": "Useful Lens", "definition": "A way to think.", "chapterIds": ["ch01"]}]
            }), encoding="utf-8")

            skill_dir = generate_book_skill.generate_book_skill(analysis, root / "skills")

            self.assertTrue((skill_dir / "SKILL.md").exists())
            self.assertTrue((skill_dir / "references" / "knowledge.md").exists())
            self.assertIn("name: demo-book-knowledge", (skill_dir / "SKILL.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
