import unittest

from app.language_router import detect_language


class TestLanguageRouterEdgeCases(unittest.TestCase):

    def test_extensionless_filename(self):
        self.assertEqual(
            detect_language("README"),
            "Unknown",
        )

    def test_empty_filename(self):
        self.assertEqual(
            detect_language(""),
            "Unknown",
        )

    def test_path_with_dotted_directory(self):
        self.assertEqual(
            detect_language(
                "folder.with.dots/script.py"
            ),
            "Python",
        )


if __name__ == "__main__":
    unittest.main()
