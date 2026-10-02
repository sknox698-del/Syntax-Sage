import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.project_scanner import scan_project


class TestProjectScanner(unittest.TestCase):

    def test_scans_supported_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            (root / "main.py").write_text(
                'print("Hello")',
                encoding="utf-8",
            )

            (root / "database.sql").write_text(
                "SELECT * FROM users;",
                encoding="utf-8",
            )

            (root / "notes.txt").write_text(
                "Ignore me",
                encoding="utf-8",
            )

            files, error = scan_project(root)

            self.assertIsNone(error)

            languages = {
                file_info["language"]
                for file_info in files
            }

            self.assertEqual(
                languages,
                {"Python", "SQL"},
            )

    def test_missing_project_folder(self):
        files, error = scan_project(
            "folder_that_does_not_exist"
        )

        self.assertIsNone(files)
        self.assertEqual(
            error,
            "Project folder not found.",
        )

    def test_project_path_must_be_folder(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "example.py"

            file_path.write_text(
                'print("Hello")',
                encoding="utf-8",
            )

            files, error = scan_project(file_path)

            self.assertIsNone(files)
            self.assertEqual(
                error,
                "The project path is not a folder.",
            )

    def test_ignored_directories_are_skipped(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            ignored = root / "node_modules"
            ignored.mkdir()

            (ignored / "library.js").write_text(
                'console.log("Ignore me");',
                encoding="utf-8",
            )

            (root / "app.js").write_text(
                'console.log("Use me");',
                encoding="utf-8",
            )

            files, error = scan_project(root)

            self.assertIsNone(error)
            self.assertEqual(len(files), 1)
            self.assertEqual(
                files[0]["language"],
                "JavaScript",
            )

    def test_skips_symbolic_linked_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            (root / "main.py").write_text(
                "print('Hello')",
                encoding="utf-8",
            )

            simulated_link = root / "external_link.py"
            simulated_link.write_text(
                "print('External')",
                encoding="utf-8",
            )

            original_is_symlink = Path.is_symlink

            def fake_is_symlink(path):
                if path.name == "external_link.py":
                    return True
                return original_is_symlink(path)

            with patch.object(
                Path,
                "is_symlink",
                fake_is_symlink,
            ):
                files, error = scan_project(str(root))

            self.assertIsNone(error)

            names = {
                Path(file_info["path"]).name
                for file_info in files
            }

            self.assertIn("main.py", names)
            self.assertNotIn("external_link.py", names)


if __name__ == "__main__":
    unittest.main()