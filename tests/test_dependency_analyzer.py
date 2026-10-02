import unittest

from app.dependency_analyzer import (
    build_dependency_map,
    build_reverse_dependency_map,
    find_affected_files,
    get_change_impact,
)


class TestDependencyAnalyzer(unittest.TestCase):

    def test_detects_local_python_dependency(self):
        project_files = [
            {
                "path": "project/main.py",
                "language": "Python",
                "analysis": {
                    "imports": ["language_router", "os"],
                },
            },
            {
                "path": "project/language_router.py",
                "language": "Python",
                "analysis": {
                    "imports": [],
                },
            },
        ]

        result = build_dependency_map(project_files)

        self.assertEqual(
            result["project/main.py"],
            ["project/language_router.py"],
        )

    def test_ignores_external_imports(self):
        project_files = [
            {
                "path": "project/main.py",
                "language": "Python",
                "analysis": {
                    "imports": ["os", "json", "pathlib"],
                },
            },
        ]

        result = build_dependency_map(project_files)

        self.assertEqual(
            result["project/main.py"],
            [],
        )

    def test_does_not_create_self_dependency(self):
        project_files = [
            {
                "path": "project/main.py",
                "language": "Python",
                "analysis": {
                    "imports": ["main"],
                },
            },
        ]

        result = build_dependency_map(project_files)

        self.assertEqual(
            result["project/main.py"],
            [],
        )

    def test_non_python_files_are_ignored(self):
        project_files = [
            {
                "path": "project/app.js",
                "language": "JavaScript",
                "analysis": {
                    "imports": ["helper"],
                },
            },
        ]

        result = build_dependency_map(project_files)

        self.assertEqual(result, {})

    def test_builds_reverse_dependency_map(self):
        dependency_map = {
            "project/main.py": [
                "project/language_router.py",
                "project/code_analyzer.py",
            ],
            "project/language_router.py": [],
            "project/code_analyzer.py": [],
        }

        result = build_reverse_dependency_map(dependency_map)

        self.assertEqual(
            result["project/language_router.py"],
            ["project/main.py"],
        )

        self.assertEqual(
            result["project/code_analyzer.py"],
            ["project/main.py"],
        )

    def test_reverse_map_handles_multiple_dependents(self):
        dependency_map = {
            "project/main.py": ["project/helper.py"],
            "project/worker.py": ["project/helper.py"],
            "project/helper.py": [],
        }

        result = build_reverse_dependency_map(dependency_map)

        self.assertEqual(
            result["project/helper.py"],
            [
                "project/main.py",
                "project/worker.py",
            ],
        )

    def test_finds_directly_affected_file(self):
        reverse_dependency_map = {
            "project/helper.py": [
                "project/main.py",
            ],
            "project/main.py": [],
        }

        result = find_affected_files(
            "project/helper.py",
            reverse_dependency_map,
        )

        self.assertEqual(
            result,
            ["project/main.py"],
        )

    def test_finds_transitively_affected_files(self):
        reverse_dependency_map = {
            "project/helper.py": [
                "project/main.py",
            ],
            "project/main.py": [
                "project/app.py",
            ],
            "project/app.py": [],
        }

        result = find_affected_files(
            "project/helper.py",
            reverse_dependency_map,
        )

        self.assertEqual(
            result,
            [
                "project/app.py",
                "project/main.py",
            ],
        )


    def test_get_change_impact_returns_affected_files(self):
        project_files = [
            {
                "path": "project/main.py",
                "language": "Python",
                "analysis": {
                    "imports": ["helper"],
                },
            },
            {
                "path": "project/helper.py",
                "language": "Python",
                "analysis": {
                    "imports": [],
                },
            },
        ]

        result = get_change_impact(
            "project/helper.py",
            project_files,
        )

        self.assertTrue(result["found"])

        self.assertEqual(
            result["target"],
            "project/helper.py",
        )

        self.assertEqual(
            result["affected_files"],
            ["project/main.py"],
        )


    def test_get_change_impact_reports_unknown_file(self):
        project_files = [
            {
                "path": "project/main.py",
                "language": "Python",
                "analysis": {
                    "imports": [],
                },
            },
        ]

        result = get_change_impact(
            "project/missing.py",
            project_files,
        )

        self.assertFalse(result["found"])

        self.assertEqual(
            result["affected_files"],
            [],
        )


    def test_detects_package_qualified_dependency(self):
        project_files = [
            {
                "path": "app/main.py",
                "language": "Python",
                "analysis": {
                    "imports": [
                        "app.project_reporter",
                    ],
                },
            },
            {
                "path": "app/project_reporter.py",
                "language": "Python",
                "analysis": {
                    "imports": [],
                },
            },
        ]

        result = build_dependency_map(
            project_files
        )

        self.assertEqual(
            result["app/main.py"],
            ["app/project_reporter.py"],
        )


    def test_package_resolution_preserves_simple_imports(self):
        project_files = [
            {
                "path": (
                    "projects/dependency_project/"
                    "main.py"
                ),
                "language": "Python",
                "analysis": {
                    "imports": ["helper"],
                },
            },
            {
                "path": (
                    "projects/dependency_project/"
                    "helper.py"
                ),
                "language": "Python",
                "analysis": {
                    "imports": [],
                },
            },
        ]

        result = build_dependency_map(
            project_files
        )

        self.assertEqual(
            result[
                "projects/dependency_project/main.py"
            ],
            [
                "projects/dependency_project/helper.py"
            ],
        )


if __name__ == "__main__":
    unittest.main()