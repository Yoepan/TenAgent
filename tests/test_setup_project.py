"""setup_project.py copies the framework into a folder the operator names.

It used to delete and replace any existing assets/, dashboard/ and .agents/
directories in that folder (and overwrite .gitignore, LICENSE, AGENTS.md ...)
without asking, and pointing it at the framework checkout itself deleted the
sources it was about to copy.  Everything here runs on throw-away trees.
"""

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(os.environ.get("TENAGENT_TEST_ROOT") or Path(__file__).resolve().parents[1])
sys.path.insert(0, str(ROOT))

import setup_project  # noqa: E402


def write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class SetupProjectTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="tenagent-setup-")
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        self.source = base / "framework"
        write(self.source / "AGENTS.md", "framework agents")
        write(self.source / "LICENSE", "framework license")
        write(self.source / ".gitignore", "framework ignore")
        write(self.source / "dashboard" / "serve.py", "framework dashboard")
        write(self.source / "assets" / "logo.txt", "framework assets")
        write(self.source / "specs" / "swarm-config.example.json", "{}")
        self.target = base / "my-existing-app"
        self.original_root = setup_project.SOURCE_ROOT
        setup_project.SOURCE_ROOT = str(self.source)
        self.addCleanup(setattr, setup_project, "SOURCE_ROOT", self.original_root)

    def run_setup(self, target, **kwargs):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            try:
                result = setup_project.bootstrap_new_project(str(target), **kwargs)
            except SystemExit as exc:
                result = exc.code
        return result, out.getvalue()

    def test_fresh_folder_gets_the_framework(self):
        result, _ = self.run_setup(self.target)
        self.assertTrue(result)
        self.assertEqual((self.target / "dashboard" / "serve.py").read_text("utf-8"), "framework dashboard")
        status = json.loads((self.target / "specs" / "swarm-status.json").read_text("utf-8"))
        self.assertEqual(status["project"]["name"], "my-existing-app")

    def test_existing_directories_are_not_deleted(self):
        write(self.target / "assets" / "precious.png", "my images")
        write(self.target / "dashboard" / "app.js", "my dashboard code")
        result, output = self.run_setup(self.target)
        self.assertFalse(result)
        self.assertIn("assets", output)
        self.assertIn("--overwrite", output)
        self.assertEqual((self.target / "assets" / "precious.png").read_text("utf-8"), "my images")
        self.assertEqual((self.target / "dashboard" / "app.js").read_text("utf-8"), "my dashboard code")
        self.assertFalse((self.target / "AGENTS.md").exists(), "nothing may be copied on refusal")
        self.assertFalse((self.target / "specs").exists())

    def test_existing_files_are_not_overwritten(self):
        for name in (".gitignore", "LICENSE", "AGENTS.md"):
            write(self.target / name, f"mine: {name}")
        result, _ = self.run_setup(self.target)
        self.assertFalse(result)
        for name in (".gitignore", "LICENSE", "AGENTS.md"):
            self.assertEqual((self.target / name).read_text("utf-8"), f"mine: {name}")

    def test_an_existing_status_file_is_not_replaced(self):
        write(self.target / "specs" / "swarm-status.json", '{"mine": true}')
        result, output = self.run_setup(self.target)
        self.assertFalse(result)
        self.assertIn("specs/swarm-status.json", output)
        self.assertEqual((self.target / "specs" / "swarm-status.json").read_text("utf-8"), '{"mine": true}')

    def test_overwrite_flag_replaces_what_conflicts(self):
        write(self.target / "assets" / "precious.png", "my images")
        write(self.target / "LICENSE", "mine")
        result, _ = self.run_setup(self.target, overwrite=True)
        self.assertTrue(result)
        self.assertFalse((self.target / "assets" / "precious.png").exists())
        self.assertEqual((self.target / "LICENSE").read_text("utf-8"), "framework license")

    def test_target_must_not_be_or_contain_the_framework_checkout(self):
        for target in (self.source, self.source / "nested", self.source / "dashboard" / "sub"):
            for overwrite in (False, True):
                with self.subTest(target=str(target.relative_to(self.source.parent)), overwrite=overwrite):
                    result, _ = self.run_setup(target, overwrite=overwrite)
                    self.assertFalse(result)
                    self.assertEqual((self.source / "dashboard" / "serve.py").read_text("utf-8"),
                                     "framework dashboard")
                    self.assertEqual((self.source / "assets" / "logo.txt").read_text("utf-8"),
                                     "framework assets")

    def test_target_that_is_a_file_is_refused(self):
        write(self.target, "i am a file")
        result, _ = self.run_setup(self.target)
        self.assertFalse(result)
        self.assertEqual(self.target.read_text("utf-8"), "i am a file")

    def test_command_line_exit_codes(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(setup_project.main([]), 1)
            write(self.target / "assets" / "x.txt", "mine")
            self.assertEqual(setup_project.main([str(self.target)]), 2)
            self.assertEqual(setup_project.main([str(self.target), "--overwrite"]), 0)


if __name__ == "__main__":
    unittest.main()
