import unittest

from app.language_router import detect_language


class TestLanguageRouter(unittest.TestCase):

    def test_python_file(self):
        self.assertEqual(detect_language("main.py"), "Python")

    def test_javascript_file(self):
        self.assertEqual(detect_language("server.js"), "JavaScript")

    def test_cpp_file(self):
        self.assertEqual(detect_language("engine.cpp"), "C++")

    def test_csharp_file(self):
        self.assertEqual(detect_language("Program.cs"), "C#")

    def test_sql_file(self):
        self.assertEqual(detect_language("database.sql"), "SQL")

    def test_unknown_file(self):
        self.assertEqual(detect_language("photo.jpg"), "Unknown")

    def test_uppercase_extension(self):
        self.assertEqual(detect_language("SCRIPT.PY"), "Python")


if __name__ == "__main__":
    unittest.main()