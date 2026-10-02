import unittest

from app.context_manager import (
    MAX_FILE_CHARACTERS,
    MAX_PROJECT_CHARACTERS,
    build_project_context,
    trim_content,
)


class TestContextManager(unittest.TestCase):

    def test_short_content_is_not_trimmed(self):
        content = "Hello"

        result, was_trimmed = trim_content(content)

        self.assertEqual(result, "Hello")
        self.assertFalse(was_trimmed)

    def test_large_file_is_trimmed(self):
        content = "A" * (MAX_FILE_CHARACTERS + 100)

        result, was_trimmed = trim_content(content)

        self.assertEqual(
            len(result),
            MAX_FILE_CHARACTERS,
        )
        self.assertTrue(was_trimmed)

    def test_project_context_respects_total_limit(self):
        project_files = []

        for index in range(10):
            project_files.append(
                {
                    "path": f"file_{index}.py",
                    "language": "Python",
                    "analysis": {},
                    "content": "A" * 4000,
                }
            )

        context = build_project_context(project_files)

        self.assertLessEqual(
            context["total_characters"],
            MAX_PROJECT_CHARACTERS,
        )

        self.assertEqual(
            context["files_available"],
            10,
        )

        self.assertLess(
            context["files_included"],
            context["files_available"],
        )

    def test_context_marks_trimmed_files(self):
        project_files = [
            {
                "path": "large.py",
                "language": "Python",
                "analysis": {},
                "content": "A" * 5000,
            }
        ]

        context = build_project_context(project_files)

        self.assertTrue(
            context["files"][0]["trimmed"]
        )

    def test_priority_files_are_included_first(self):
        project_files = [
            {
                "path": "random.py",
                "language": "Python",
                "analysis": {},
                "content": "A" * 4000,
            },
            {
                "path": "main.py",
                "language": "Python",
                "analysis": {},
                "content": "B" * 4000,
            },
            {
                "path": "helper.py",
                "language": "Python",
                "analysis": {},
                "content": "C" * 4000,
            },
        ]

        context = build_project_context(project_files)

        self.assertEqual(
            context["files"][0]["path"],
            "main.py",
        )

    def test_smaller_files_are_preferred_with_same_priority(self):
        project_files = [
            {
                "path": "large.py",
                "language": "Python",
                "analysis": {},
                "content": "A" * 4000,
            },
            {
                "path": "small.py",
                "language": "Python",
                "analysis": {},
                "content": "B" * 100,
            },
        ]

        context = build_project_context(project_files)

        self.assertEqual(
            context["files"][0]["path"],
            "small.py",
        )

    def test_trimmed_files_are_reported(self):
        project_files = [
            {
                "path": "large.py",
                "language": "Python",
                "analysis": {},
                "content": "A" * 5000,
            }
        ]

        context = build_project_context(project_files)

        self.assertIn(
            "large.py",
            context["trimmed_files"],
        )

    def test_omitted_files_are_reported(self):
        project_files = []

        for index in range(5):
            project_files.append(
                {
                    "path": f"file_{index}.py",
                    "language": "Python",
                    "analysis": {},
                    "content": "A" * 4000,
                }
            )

        context = build_project_context(project_files)

        self.assertGreater(
            len(context["omitted_files"]),
            0,
        )

    def test_preferred_file_survives_tight_budget(self):
        project_files = [
            {
                "path": "app/main.py",
                "language": "Python",
                "content": "M" * 4000,
            },
            {
                "path": "app/dependency_analyzer.py",
                "language": "Python",
                "content": "D" * 3500,
            },
        ]

        for index in range(10):
            project_files.append(
                {
                    "path": f"app/small_{index}.py",
                    "language": "Python",
                    "content": "S" * 1000,
                }
            )

        context = build_project_context(
            project_files,
            preferred_paths=[
                "app/dependency_analyzer.py"
            ],
        )

        included = {
            item["path"]: item
            for item in context["files"]
        }

        self.assertIn(
            "app/dependency_analyzer.py",
            included,
        )

        self.assertEqual(
            len(
                included[
                    "app/dependency_analyzer.py"
                ]["content"]
            ),
            3500,
        )

        self.assertLessEqual(
            context["total_characters"],
            MAX_PROJECT_CHARACTERS,
        )

    def test_preferred_paths_accept_windows_separators(self):
        project_files = [
            {
                "path": "app\\main.py",
                "language": "Python",
                "content": "M" * 100,
            },
            {
                "path": "app\\dependency_analyzer.py",
                "language": "Python",
                "content": "D" * 100,
            },
        ]

        context = build_project_context(
            project_files,
            preferred_paths=[
                "app/dependency_analyzer.py"
            ],
        )

        self.assertEqual(
            context["files"][0]["path"],
            "app\\dependency_analyzer.py",
        )

    def test_preferred_file_can_exceed_standard_file_limit(self):
        source = "A" * 4084

        files = [
            {
                "path": "app/dependency_analyzer.py",
                "language": "Python",
                "analysis": {},
                "content": source,
            }
        ]

        normal = build_project_context(files)

        preferred = build_project_context(
            files,
            preferred_paths=[
                "app/dependency_analyzer.py",
            ],
        )

        # Existing default behavior must remain unchanged.
        self.assertEqual(
            len(normal["files"][0]["content"]),
            4000,
        )
        self.assertTrue(normal["files"][0]["trimmed"])

        # Explicitly requested source should be complete.
        self.assertEqual(
            preferred["files"][0]["content"],
            source,
        )
        self.assertFalse(
            preferred["files"][0]["trimmed"]
        )

        # The overall project limit still applies.
        self.assertLessEqual(
            preferred["total_characters"],
            MAX_PROJECT_CHARACTERS,
        )


if __name__ == "__main__":
    unittest.main()