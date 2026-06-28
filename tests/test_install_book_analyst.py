import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "scripts" / "install-book-analyst"
SKILL_SOURCE = ROOT / "skill" / "book-analyst"


class InstallBookAnalystTests(unittest.TestCase):
    def test_installs_skill_package_and_prints_activation_prompt(self):
        with tempfile.TemporaryDirectory() as tmp:
            skills_dir = Path(tmp) / "skills"
            installed = skills_dir / "book-analyst"

            result = subprocess.run(
                [
                    str(INSTALLER),
                    "--skills-dir",
                    str(skills_dir),
                    "--source",
                    str(SKILL_SOURCE),
                ],
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((installed / "SKILL.md").exists())
            self.assertTrue((installed / "scripts" / "init_project.py").exists())
            self.assertTrue((installed / "assets" / "page-templates" / "library-empty.html").exists())
            self.assertIn("name: book-analyst", (installed / "SKILL.md").read_text(encoding="utf-8"))
            self.assertIn("Use $book-analyst", result.stdout)

    def test_replaces_stale_existing_install(self):
        with tempfile.TemporaryDirectory() as tmp:
            skills_dir = Path(tmp) / "skills"
            installed = skills_dir / "book-analyst"
            installed.mkdir(parents=True)
            (installed / "stale.txt").write_text("old", encoding="utf-8")

            result = subprocess.run(
                [
                    str(INSTALLER),
                    "--skills-dir",
                    str(skills_dir),
                    "--source",
                    str(SKILL_SOURCE),
                ],
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse((installed / "stale.txt").exists())
            self.assertTrue((installed / "SKILL.md").exists())


if __name__ == "__main__":
    unittest.main()
