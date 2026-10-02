import tempfile
import unittest
from pathlib import Path

from app.file_reader import read_code_file


class TestFileReader(unittest.TestCase):

    def test_reads_existing_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "example.py"
            test_file.write_text(
                'print("Hello")',
                encoding="utf-8",
            )

            content, error = read_code_file(test_file)

            self.assertEqual(content, 'print("Hello")')
            self.assertIsNone(error)

    def test_missing_file(self):
        content, error = read_code_file("file_that_does_not_exist.py")

        self.assertIsNone(content)
        self.assertEqual(error, "File not found.")

    def test_directory_is_not_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            content, error = read_code_file(temp_dir)

            self.assertIsNone(content)
            self.assertEqual(error, "The path is not a file.")


if __name__ == "__main__":
    unittest.main()