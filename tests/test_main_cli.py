import io
import unittest
from unittest.mock import patch

from app.ai_client import EXPLANATION_SYSTEM_PROMPT

from app.main import (
    analyze_single_file,
    ask_about_project,
    check_change_impact,
    main,
    scan_entire_project,
)


class TestMainCLI(unittest.TestCase):

    def setUp(self):
        self.project_files = [
            {
                "path": "projects\\dependency_project\\helper.py",
                "language": "Python",
                "analysis": {
                    "imports": [],
                },
            },
            {
                "path": "projects\\dependency_project\\main.py",
                "language": "Python",
                "analysis": {
                    "imports": ["helper"],
                },
            },
        ]

    @patch("app.main.analyze_project")
    def test_change_impact_lists_affected_file(
        self,
        mock_analyze_project,
    ):
        mock_analyze_project.return_value = (
            self.project_files,
            None,
        )

        user_input = [
            "projects\\dependency_project",
            "projects\\dependency_project\\helper.py",
        ]

        output = io.StringIO()

        with patch(
            "builtins.input",
            side_effect=user_input,
        ), patch(
            "sys.stdout",
            new=output,
        ):
            check_change_impact()

        result = output.getvalue()

        self.assertIn(
            "Potentially affected files:",
            result,
        )

        self.assertIn(
            "projects\\dependency_project\\main.py",
            result,
        )

    @patch("app.main.analyze_project")
    def test_change_impact_reports_no_affected_files(
        self,
        mock_analyze_project,
    ):
        mock_analyze_project.return_value = (
            self.project_files,
            None,
        )

        user_input = [
            "projects\\dependency_project",
            "projects\\dependency_project\\main.py",
        ]

        output = io.StringIO()

        with patch(
            "builtins.input",
            side_effect=user_input,
        ), patch(
            "sys.stdout",
            new=output,
        ):
            check_change_impact()

        result = output.getvalue()

        self.assertIn(
            "No other project files are currently affected by this file.",
            result,
        )

    @patch("app.main.analyze_project")
    def test_change_impact_reports_unknown_file(
        self,
        mock_analyze_project,
    ):
        mock_analyze_project.return_value = (
            self.project_files,
            None,
        )

        user_input = [
            "projects\\dependency_project",
            "projects\\dependency_project\\missing.py",
        ]

        output = io.StringIO()

        with patch(
            "builtins.input",
            side_effect=user_input,
        ), patch(
            "sys.stdout",
            new=output,
        ):
            check_change_impact()

        result = output.getvalue()

        self.assertIn(
            "The requested file was not found "
            "in the analyzed dependency map.",
            result,
        )

    def test_main_menu_option_five_exits_cleanly(self):
        output = io.StringIO()

        with patch(
            "builtins.input",
            return_value="5",
        ), patch(
            "sys.stdout",
            new=output,
        ):
            main()

        result = output.getvalue()

        self.assertIn(
            "3. Check change impact",
            result,
        )

        self.assertIn(
            "5. Exit",
            result,
        )

        self.assertIn(
            "Syntax Sage shutting down.",
            result,
        )


    @patch("app.main.stream_ai")
    @patch("app.main.analyze_project")
    def test_problem_question_bypasses_ai(
        self,
        mock_analyze_project,
        mock_stream_ai,
    ):
        mock_analyze_project.return_value = (
            self.project_files,
            None,
        )

        user_input = [
            "projects\\dependency_project",
            "Is anything broken in this project?",
        ]

        output = io.StringIO()

        with patch(
            "builtins.input",
            side_effect=user_input,
        ), patch(
            "sys.stdout",
            new=output,
        ):
            ask_about_project()

        result = output.getvalue()

        self.assertIn(
            "No confirmed real problems found.",
            result,
        )

        mock_stream_ai.assert_not_called()


    @patch("app.main.stream_ai")
    @patch("app.main.analyze_project")
    def test_pure_change_impact_question_bypasses_ai(
        self,
        mock_analyze_project,
        mock_stream_ai,
    ):
        mock_analyze_project.return_value = (
            self.project_files,
            None,
        )

        user_input = [
            "projects\\dependency_project",
            "What could be affected if I change helper.py?",
        ]

        output = io.StringIO()

        with patch(
            "builtins.input",
            side_effect=user_input,
        ), patch(
            "sys.stdout",
            new=output,
        ):
            ask_about_project()

        result = output.getvalue()

        self.assertIn(
            "Changing helper.py could affect:",
            result,
        )

        self.assertIn(
            "projects\\dependency_project\\main.py",
            result,
        )

        self.assertNotIn(
            "will affect",
            result.lower(),
        )

        mock_stream_ai.assert_not_called()


    @patch("app.main.stream_ai")
    @patch("app.main.analyze_project")
    def test_mixed_question_appends_verified_change_impact(
        self,
        mock_analyze_project,
        mock_stream_ai,
    ):
        mock_analyze_project.return_value = (
            self.project_files,
            None,
        )

        mock_stream_ai.return_value = iter(
            [
                "helper.py defines the greet(name) function."
            ]
        )

        user_input = [
            "projects\\dependency_project",
            (
                "What does helper.py do, and what could "
                "be affected if I change it?"
            ),
        ]

        output = io.StringIO()

        with patch(
            "builtins.input",
            side_effect=user_input,
        ), patch(
            "sys.stdout",
            new=output,
        ):
            ask_about_project()

        result = output.getvalue()

        self.assertIn(
            "helper.py defines the greet(name) function.",
            result,
        )

        self.assertIn(
            "Verified change impact:",
            result,
        )

        self.assertIn(
            "Changing helper.py could affect:",
            result,
        )

        self.assertIn(
            "projects\\dependency_project\\main.py",
            result,
        )

        mock_stream_ai.assert_called_once()


    @patch("app.main.stream_ai")
    @patch("app.main.analyze_project")
    def test_general_project_question_uses_ai(
        self,
        mock_analyze_project,
        mock_stream_ai,
    ):
        mock_analyze_project.return_value = (
            self.project_files,
            None,
        )

        mock_stream_ai.return_value = iter(
            [
                "helper.py defines a greeting function."
            ]
        )

        user_input = [
            "projects\\dependency_project",
            "What does helper.py do?",
        ]

        output = io.StringIO()

        with patch(
            "builtins.input",
            side_effect=user_input,
        ), patch(
            "sys.stdout",
            new=output,
        ):
            ask_about_project()

        result = output.getvalue()

        self.assertIn(
            "helper.py defines a greeting function.",
            result,
        )

        self.assertNotIn(
            "Verified change impact:",
            result,
        )

        mock_stream_ai.assert_called_once()


    @patch("app.main.stream_ai")
    @patch("app.main.analyze_project")
    def test_general_question_removes_unsolicited_improvements(
        self,
        mock_analyze_project,
        mock_stream_ai,
    ):
        mock_analyze_project.return_value = (
            self.project_files,
            None,
        )

        mock_stream_ai.return_value = iter(
            [
                (
                    "helper.py defines greet(name).\n\n"
                    "Optional improvements:\n"
                    "- Add a docstring.\n"
                    "- Add type hints."
                )
            ]
        )

        user_input = [
            "projects\\dependency_project",
            "What does helper.py do?",
        ]

        output = io.StringIO()

        with patch(
            "builtins.input",
            side_effect=user_input,
        ), patch(
            "sys.stdout",
            new=output,
        ):
            ask_about_project()

        result = output.getvalue()

        self.assertIn(
            "helper.py defines greet(name).",
            result,
        )

        self.assertNotIn(
            "Optional improvements",
            result,
        )

        self.assertNotIn(
            "Add a docstring",
            result,
        )

        self.assertNotIn(
            "Add type hints",
            result,
        )


    @patch("app.main.stream_ai")
    @patch("app.main.analyze_project")
    def test_general_question_removes_unsolicited_code(
        self,
        mock_analyze_project,
        mock_stream_ai,
    ):
        mock_analyze_project.return_value = (
            self.project_files,
            None,
        )

        mock_stream_ai.return_value = iter(
            [
                (
                    "helper.py defines a greeting function.\n\n"
                    "```python\n"
                    "def greet(name):\n"
                    "    return f'Hello, {name}'\n"
                    "```"
                )
            ]
        )

        user_input = [
            "projects\\dependency_project",
            "What does helper.py do?",
        ]

        output = io.StringIO()

        with patch(
            "builtins.input",
            side_effect=user_input,
        ), patch(
            "sys.stdout",
            new=output,
        ):
            ask_about_project()

        result = output.getvalue()

        self.assertIn(
            "helper.py defines a greeting function.",
            result,
        )

        self.assertNotIn(
            "def greet",
            result,
        )

        self.assertNotIn(
            "```",
            result,
        )


    @patch("app.main.stream_ai")
    @patch("app.main.analyze_project")
    def test_requested_code_is_preserved(
        self,
        mock_analyze_project,
        mock_stream_ai,
    ):
        mock_analyze_project.return_value = (
            self.project_files,
            None,
        )

        mock_stream_ai.return_value = iter(
            [
                (
                    "```python\n"
                    "def greet(name):\n"
                    "    return f'Hello, {name}'\n"
                    "```"
                )
            ]
        )

        user_input = [
            "projects\\dependency_project",
            "Show me code for the greet function.",
        ]

        output = io.StringIO()

        with patch(
            "builtins.input",
            side_effect=user_input,
        ), patch(
            "sys.stdout",
            new=output,
        ):
            ask_about_project()

        result = output.getvalue()

        self.assertIn(
            "def greet",
            result,
        )

        self.assertIn(
            "```python",
            result,
        )


    @patch("app.main.stream_ai")
    @patch("app.main.analyze_project")
    def test_requested_improvements_are_preserved(
        self,
        mock_analyze_project,
        mock_stream_ai,
    ):
        mock_analyze_project.return_value = (
            self.project_files,
            None,
        )

        mock_stream_ai.return_value = iter(
            [
                (
                    "Optional improvements:\n"
                    "- Add a docstring.\n"
                    "- Add type hints."
                )
            ]
        )

        user_input = [
            "projects\\dependency_project",
            "What improvements would you suggest?",
        ]

        output = io.StringIO()

        with patch(
            "builtins.input",
            side_effect=user_input,
        ), patch(
            "sys.stdout",
            new=output,
        ):
            ask_about_project()

        result = output.getvalue()

        self.assertIn(
            "Optional improvements",
            result,
        )

        self.assertIn(
            "Add a docstring",
            result,
        )


    @patch("app.main.stream_ai")
    @patch("app.main.build_project_review_prompt")
    @patch("app.main.build_project_report")
    @patch("app.main.build_project_context")
    @patch("app.main.analyze_project")
    def test_project_scan_guard_replaces_contradictory_ai_review(
        self,
        mock_analyze_project,
        mock_build_context,
        mock_build_report,
        mock_build_prompt,
        mock_stream_ai,
    ):
        project_files = [
            {
                "path": "project/broken.py",
                "language": "Python",
                "content": "def broken(\n",
                "analysis": {
                    "total_lines": 1,
                    "code_lines": 1,
                    "blank_lines": 0,
                    "syntax_valid": False,
                    "syntax_error": "Line 1: '(' was never closed",
                    "imports": [],
                    "functions": [],
                    "classes": [],
                    "methods": [],
                },
            },
        ]

        mock_analyze_project.return_value = (
            project_files,
            None,
        )

        mock_build_context.return_value = {
            "files": project_files,
            "files_available": 1,
            "files_included": 1,
            "total_characters": 12,
            "trimmed_files": [],
            "omitted_files": [],
        }

        mock_build_report.return_value = (
            "Verified report placeholder"
        )

        mock_build_prompt.return_value = (
            "Project review prompt"
        )

        mock_stream_ai.return_value = iter(
            [
                (
                    "5. Real problems\n\n"
                    "No real problems found.\n\n"
                    "6. Optional improvements\n\n"
                    "No optional improvements recommended."
                )
            ]
        )

        output = io.StringIO()

        with patch(
            "builtins.input",
            return_value="project",
        ), patch(
            "sys.stdout",
            new=output,
        ):
            scan_entire_project()

        result = output.getvalue()

        self.assertIn(
            "5. Real problems",
            result,
        )

        self.assertIn(
            "project/broken.py",
            result,
        )

        self.assertIn(
            "never closed",
            result,
        )

        self.assertNotIn(
            "No real problems found.",
            result,
        )


    @patch("app.main.stream_ai")
    @patch("app.main.build_project_review_prompt")
    @patch("app.main.build_project_report")
    @patch("app.main.build_project_context")
    @patch("app.main.analyze_project")
    def test_project_scan_keeps_ai_review_when_no_verified_errors(
        self,
        mock_analyze_project,
        mock_build_context,
        mock_build_report,
        mock_build_prompt,
        mock_stream_ai,
    ):
        project_files = [
            {
                "path": "project/good.py",
                "language": "Python",
                "content": "print('hello')",
                "analysis": {
                    "total_lines": 1,
                    "code_lines": 1,
                    "blank_lines": 0,
                    "syntax_valid": True,
                    "imports": [],
                    "functions": [],
                    "classes": [],
                    "methods": [],
                },
            },
        ]

        mock_analyze_project.return_value = (
            project_files,
            None,
        )

        mock_build_context.return_value = {
            "files": project_files,
            "files_available": 1,
            "files_included": 1,
            "total_characters": 14,
            "trimmed_files": [],
            "omitted_files": [],
        }

        mock_build_report.return_value = (
            "Verified report placeholder"
        )

        mock_build_prompt.return_value = (
            "Project review prompt"
        )

        mock_stream_ai.return_value = iter(
            [
                (
                    "5. Real problems\n\n"
                    "No real problems found.\n\n"
                    "6. Optional improvements\n\n"
                    "No optional improvements recommended."
                )
            ]
        )

        output = io.StringIO()

        with patch(
            "builtins.input",
            return_value="project",
        ), patch(
            "sys.stdout",
            new=output,
        ):
            scan_entire_project()

        result = output.getvalue()

        self.assertIn(
            "No real problems found.",
            result,
        )


    def _scanner_test_project_files(self):
        return [
            {
                "path": "app/project_scanner.py",
                "language": "Python",
                "content": "def scan_project(path):\n    return []",
                "analysis": {
                    "total_lines": 2,
                    "code_lines": 2,
                    "blank_lines": 0,
                    "syntax_valid": True,
                    "imports": [],
                    "functions": [
                        {"name": "scan_project", "line": 1}
                    ],
                    "classes": [],
                    "methods": [],
                },
            },
            {
                "path": "tests/test_project_scanner.py",
                "language": "Python",
                "content": (
                    "import unittest\n"
                    "from app.project_scanner import scan_project\n\n"
                    "class TestProjectScanner(unittest.TestCase):\n"
                    "    def test_scan_project(self):\n"
                    "        self.assertEqual(scan_project('.'), [])\n"
                ),
                "analysis": {
                    "total_lines": 6,
                    "code_lines": 5,
                    "blank_lines": 1,
                    "syntax_valid": True,
                    "imports": [
                        "unittest",
                        "app.project_scanner",
                    ],
                    "functions": [],
                    "classes": [
                        {"name": "TestProjectScanner", "line": 4}
                    ],
                    "methods": [
                        {
                            "class": "TestProjectScanner",
                            "name": "test_scan_project",
                            "line": 5,
                        }
                    ],
                },
            },
        ]

    def _run_project_review(self, project_files, ai_response):
        context = {
            "files": project_files,
            "files_available": len(project_files),
            "files_included": len(project_files),
            "total_characters": sum(
                len(file_info["content"])
                for file_info in project_files
            ),
            "trimmed_files": [],
            "omitted_files": [],
        }

        output = io.StringIO()

        with patch(
            "app.main.analyze_project",
            return_value=(project_files, None),
        ), patch(
            "app.main.build_project_context",
            return_value=context,
        ), patch(
            "app.main.build_project_report",
            return_value="Verified report placeholder",
        ), patch(
            "app.main.build_project_review_prompt",
            return_value="Project review prompt",
        ), patch(
            "app.main.stream_ai",
            return_value=iter([ai_response]),
        ), patch(
            "builtins.input",
            return_value=".",
        ), patch(
            "sys.stdout",
            new=output,
        ):
            scan_entire_project()

        return output.getvalue()

    def test_cli_filters_false_test_absence_advice(self):
        project_files = self._scanner_test_project_files()

        ai_response = (
            "5. Real problems\n\n"
            "No real problems found.\n\n"
            "6. Optional improvements\n\n"
            "- There are no unit tests for scan_project."
        )

        result = self._run_project_review(
            project_files,
            ai_response,
        )

        self.assertNotIn(
            "There are no unit tests for scan_project",
            result,
        )

        self.assertIn(
            "No real problems found.",
            result,
        )

    def test_cli_preserves_errors_and_filters_false_advice(self):
        project_files = self._scanner_test_project_files()

        for path in (
            "projects/broken_example.py",
            "projects/broken_project/broken_example.py",
        ):
            project_files.append(
                {
                    "path": path,
                    "language": "Python",
                    "content": "def broken()\n    pass",
                    "analysis": {
                        "total_lines": 2,
                        "code_lines": 2,
                        "blank_lines": 0,
                        "syntax_valid": False,
                        "syntax_error": "Line 1: expected ':'",
                        "imports": [],
                        "functions": [],
                        "classes": [],
                        "methods": [],
                    },
                }
            )

        ai_response = (
            "5. Real problems\n\n"
            "No real problems found.\n\n"
            "6. Optional improvements\n\n"
            "- There are no unit tests for scan_project."
        )

        result = self._run_project_review(
            project_files,
            ai_response,
        )

        self.assertIn(
            "projects/broken_example.py",
            result,
        )

        self.assertIn(
            "projects/broken_project/broken_example.py",
            result,
        )

        self.assertEqual(
            result.count("Line 1: expected ':'"),
            2,
        )

        self.assertNotIn(
            "No real problems found.",
            result,
        )

        self.assertNotIn(
            "There are no unit tests for scan_project",
            result,
        )


    def test_cli_filters_false_function_print_advice(self):
        project_files = self._scanner_test_project_files()

        ai_response = (
            "5. Real problems\n\n"
            "No real problems found.\n\n"
            "6. Optional improvements\n\n"
            "- The `scan_project` function currently prints "
            "the results directly in the "
            "`if __name__ == \"__main__\":` block. "
            "Consider refactoring it to return results."
        )

        result = self._run_project_review(
            project_files,
            ai_response,
        )

        self.assertNotIn(
            "currently prints",
            result,
        )

        self.assertIn(
            "No real problems found.",
            result,
        )

    def test_cli_preserves_errors_while_filtering_print_advice(self):
        project_files = self._scanner_test_project_files()

        project_files.append(
            {
                "path": "projects/broken_example.py",
                "language": "Python",
                "content": "def broken()\n    pass",
                "analysis": {
                    "total_lines": 2,
                    "code_lines": 2,
                    "blank_lines": 0,
                    "syntax_valid": False,
                    "syntax_error": "Line 1: expected ':'",
                    "imports": [],
                    "functions": [],
                    "classes": [],
                    "methods": [],
                },
            }
        )

        ai_response = (
            "5. Real problems\n\n"
            "No real problems found.\n\n"
            "6. Optional improvements\n\n"
            "- The `scan_project` function currently prints "
            "the results directly in the "
            "`if __name__ == \"__main__\":` block. "
            "Consider refactoring it to return results."
        )

        result = self._run_project_review(
            project_files,
            ai_response,
        )

        self.assertIn(
            "projects/broken_example.py",
            result,
        )

        self.assertIn(
            "Line 1: expected ':'",
            result,
        )

        self.assertNotIn(
            "No real problems found.",
            result,
        )

        self.assertNotIn(
            "currently prints",
            result,
        )


    @patch("app.main.stream_ai")
    @patch("app.main.analyze_project")
    def test_single_file_explanation_uses_focused_prompt(self, mock_analyze, mock_stream):
        from app.ai_client import EXPLANATION_SYSTEM_PROMPT
        files = [
            {"path": "app/helper.py", "language": "Python", "content": "TARGET_SOURCE"},
            {"path": "app/other.py", "language": "Python", "content": "UNRELATED_SOURCE"},
        ]
        mock_analyze.return_value = (files, None)
        mock_stream.return_value = iter(["Explanation."])
        with patch("builtins.input", side_effect=["app", "Explain helper.py"]), patch("sys.stdout", new=io.StringIO()), patch("app.main.build_compact_general_question_prompt") as fallback:
            ask_about_project()
        fallback.assert_not_called()
        mock_stream.assert_called_once()
        prompt = mock_stream.call_args.args[0]
        self.assertIn("TARGET_SOURCE", prompt)
        self.assertNotIn("UNRELATED_SOURCE", prompt)
        self.assertNotIn("COMPLETE PROJECT INVENTORY", prompt)
        self.assertEqual(mock_stream.call_args.kwargs, {"system_prompt": EXPLANATION_SYSTEM_PROMPT})

    @patch("app.main.stream_ai")
    @patch("app.main.analyze_project")
    def test_unfocused_questions_keep_project_prompt(self, mock_analyze, mock_stream):
        files = [
            {"path": "app/helper.py", "language": "Python", "content": "APP_SOURCE"},
            {"path": "tests/helper.py", "language": "Python", "content": "TEST_SOURCE"},
        ]
        for question in ("Explain this project", "Explain helper.py"):
            with self.subTest(question=question):
                mock_analyze.return_value = (files, None)
                mock_stream.reset_mock()
                mock_stream.return_value = iter(["Explanation."])
                with patch("builtins.input", side_effect=["app", question]), patch("sys.stdout", new=io.StringIO()):
                    ask_about_project()
                mock_stream.assert_called_once()
                self.assertIn("PROJECT FILES:", mock_stream.call_args.args[0])
                self.assertEqual(mock_stream.call_args.kwargs, {"system_prompt": EXPLANATION_SYSTEM_PROMPT})


    @patch("app.main.stream_ai")
    @patch("app.main.analyze_project")
    def test_verified_dependency_explanation_bypasses_ai(self, mock_analyze, mock_stream):
        mock_analyze.return_value = (self.project_files, None)
        output = io.StringIO()
        with patch("builtins.input", side_effect=[
            "projects\\dependency_project",
            "Explain get_change_impact() for helper.py",
        ]), patch("sys.stdout", new=output):
            ask_about_project()

        answer = output.getvalue()
        self.assertIn("pending list starts with direct dependents", answer)
        self.assertIn("The target itself is excluded from affected_files.", answer)
        self.assertIn("Potentially affected files:", answer)
        self.assertIn("projects\\dependency_project\\main.py", answer)
        self.assertIn("get_change_impact() returns:", answer)
        self.assertIn("- found: True", answer)
        mock_stream.assert_not_called()


    @patch("app.main.stream_ai")
    @patch("app.main.analyze_project")
    def test_combined_verified_explanation_bypasses_ai(self, mock_analyze, mock_stream):
        mock_analyze.return_value = ([
            {"path": "app/dependency_analyzer.py", "language": "Python", "analysis": {"imports": []}},
            {"path": "app/main.py", "language": "Python", "analysis": {"imports": ["app.dependency_analyzer"]}},
        ], None)
        output = io.StringIO()
        with patch("builtins.input", side_effect=[
            "app",
            "Explain how dependency_analyzer.py resolves imports and traces affected files. "
            "Describe exactly what get_change_impact() returns.",
        ]), patch("sys.stdout", new=output):
            ask_about_project()
        answer = output.getvalue()
        self.assertIn("longest to shortest", answer)
        self.assertNotIn("Analyzed imports for:", answer)
        self.assertNotIn("No imports recorded", answer)
        self.assertIn("excluded from affected_files", answer)
        self.assertIn("- found: False", answer)
        self.assertIn("- target: the original requested path", answer)
        self.assertIn("Verified change impact:", answer)
        self.assertIn("Changing dependency_analyzer.py could affect:", answer)
        mock_stream.assert_not_called()


    @patch("app.main.stream_ai")
    @patch("app.main.analyze_project")
    def test_two_file_explanation_uses_compact_prompt(self, mock_analyze, mock_stream):
        from app.ai_client import EXPLANATION_SYSTEM_PROMPT
        files = [
            {"path": "app/scanner.py", "language": "Python", "content": "SCANNER_SOURCE_MARKER"},
            {"path": "app/analyzer.py", "language": "Python", "content": "ANALYZER_SOURCE_MARKER"},
            {"path": "app/other.py", "language": "Python", "content": "UNRELATED_SOURCE_MARKER"},
        ]
        mock_analyze.return_value = (files, None)
        mock_stream.return_value = iter(["The modules work together."])
        with patch("builtins.input", side_effect=["app", "Explain scanner.py and analyzer.py"]), patch("sys.stdout", new=io.StringIO()), patch("app.main.build_compact_general_question_prompt") as fallback:
            ask_about_project()
        fallback.assert_not_called()
        mock_stream.assert_called_once()
        prompt = mock_stream.call_args.args[0]
        self.assertIn("SCANNER_SOURCE_MARKER", prompt)
        self.assertIn("ANALYZER_SOURCE_MARKER", prompt)
        self.assertNotIn("UNRELATED_SOURCE_MARKER", prompt)
        self.assertNotIn("COMPLETE PROJECT INVENTORY", prompt)
        self.assertEqual(mock_stream.call_args.kwargs, {"system_prompt": EXPLANATION_SYSTEM_PROMPT})

    @patch("app.main.stream_ai")
    @patch("app.main.analyze_project")
    def test_rejected_two_file_request_uses_existing_fallback(self, mock_analyze, mock_stream):
        files = [
            {"path": "app/scanner.py", "language": "Python", "content": "A" * 4000},
            {"path": "app/analyzer.py", "language": "Python", "content": "B" * 3000},
        ]
        mock_analyze.return_value = (files, None)
        mock_stream.return_value = iter(["Project answer."])
        with patch("builtins.input", side_effect=["app", "Explain scanner.py and analyzer.py"]), patch("sys.stdout", new=io.StringIO()), patch(
            "app.main.build_compact_general_question_prompt",
            return_value="PROJECT FILES:\nCompact general answer context",
        ) as fallback:
            ask_about_project()
        fallback.assert_called_once_with(
            project_path="app",
            project_files=files,
            question="Explain scanner.py and analyzer.py",
        )
        mock_stream.assert_called_once()
        self.assertIn("PROJECT FILES:", mock_stream.call_args.args[0])
        self.assertEqual(mock_stream.call_args.kwargs, {"system_prompt": EXPLANATION_SYSTEM_PROMPT})


    @patch("app.main.stream_ai")
    @patch("app.main.analyze_project")
    def test_verified_pipeline_explanation_bypasses_ai_and_problem_router(self, mock_analyze, mock_stream):
        from app.project_pipeline_presenter import format_verified_project_pipeline
        mock_analyze.return_value = ([
            {"path": "app/project_scanner.py", "language": "Python", "analysis": {"imports": []}},
            {"path": "app/project_analyzer.py", "language": "Python", "analysis": {"imports": ["app.project_scanner"]}},
        ], None)
        question = (
            "Explain how project_scanner.py and project_analyzer.py work together. "
            "Do not perform a code review."
        )
        for query in (question, question + " Describe their error handling."):
            with self.subTest(question=query):
                output = io.StringIO()
                with patch("builtins.input", side_effect=["app", query]), patch("sys.stdout", new=output):
                    ask_about_project()
                self.assertIn(format_verified_project_pipeline(), output.getvalue())
                self.assertNotIn("No confirmed real problems found.", output.getvalue())
                mock_stream.assert_not_called()


    @patch("app.main.stream_ai")
    @patch("app.main.analyze_project")
    def test_oversized_general_question_bypasses_ai(self, mock_analyze, mock_stream):
        from app.ai_client import EXPLANATION_SYSTEM_PROMPT
        from app.qa_prompt_budget import MAX_GENERAL_REQUEST_CHARACTERS

        mock_analyze.return_value = (self.project_files, None)
        prompt = "P" * (MAX_GENERAL_REQUEST_CHARACTERS - len(EXPLANATION_SYSTEM_PROMPT) + 1)
        output = io.StringIO()
        with patch(
            "builtins.input", side_effect=["app", "Summarize this project"]
        ), patch("sys.stdout", new=output), patch(
            "app.main.build_compact_general_question_prompt", return_value=prompt
        ) as build_prompt:
            ask_about_project()

        build_prompt.assert_called_once()
        self.assertIn(
            "The general project prompt is too large "
            "for the current conservative Q&A limit.",
            output.getvalue(),
        )
        self.assertIn(
            "Try asking about one or two specific source files instead.",
            output.getvalue(),
        )
        mock_stream.assert_not_called()


    @patch("app.main.stream_ai")
    @patch("app.main.analyze_project")
    def test_broad_question_uses_compact_summary_and_explanation_system(self, mock_analyze, mock_stream):
        files = [{
            "path": "app/example.py", "language": "Python",
            "content": "SECRET_SOURCE_MARKER",
            "analysis": {"syntax_valid": True, "functions": [{"name": "run"}]},
        }]
        mock_analyze.return_value = (files, None)
        mock_stream.return_value = iter(["Architecture overview."])
        output = io.StringIO()
        with patch("builtins.input", side_effect=["app", "Give me a project overview"]), patch("sys.stdout", new=output):
            ask_about_project()
        mock_stream.assert_called_once()
        prompt = mock_stream.call_args.args[0]
        self.assertIn("PROJECT FILES:", prompt)
        self.assertIn("path=app/example.py", prompt)
        self.assertIn("functions=run", prompt)
        self.assertNotIn("SECRET_SOURCE_MARKER", prompt)
        self.assertNotIn("COMPLETE PROJECT INVENTORY", prompt)
        self.assertEqual(mock_stream.call_args.kwargs, {"system_prompt": EXPLANATION_SYSTEM_PROMPT})
        self.assertIn("Architecture overview.", output.getvalue())

    @patch("app.main.stream_ai")
    @patch("app.main.analyze_project")
    def test_compact_general_budget_boundary(self, mock_analyze, mock_stream):
        from app.qa_prompt_budget import MAX_GENERAL_REQUEST_CHARACTERS
        mock_analyze.return_value = (self.project_files, None)
        for extra in (0, 1):
            with self.subTest(extra=extra):
                mock_stream.reset_mock()
                mock_stream.return_value = iter(["Overview."])
                prompt = "P" * (MAX_GENERAL_REQUEST_CHARACTERS - len(EXPLANATION_SYSTEM_PROMPT) + extra)
                output = io.StringIO()
                with patch("builtins.input", side_effect=["app", "Give me a project overview"]), patch("sys.stdout", new=output), patch("app.main.build_compact_general_question_prompt", return_value=prompt):
                    ask_about_project()
                if extra:
                    mock_stream.assert_not_called()
                    self.assertIn("general project prompt is too large", output.getvalue())
                else:
                    mock_stream.assert_called_once_with(prompt, system_prompt=EXPLANATION_SYSTEM_PROMPT)
                    self.assertIn("Overview.", output.getvalue())


    @patch("app.main.stream_ai")
    @patch("app.main.analyze_project")
    def test_verified_structural_architecture_bypasses_ai(self, mock_analyze, mock_stream):
        mock_analyze.return_value = (self.project_files, None)
        question = (
            "Give me a verified structural overview of this project's architecture. "
            "Show the modules, discovered symbols, and static dependency relationships. "
            "Do not infer runtime execution order, module responsibilities, or data flow."
        )
        output = io.StringIO()
        with patch("builtins.input", side_effect=["app", question]), patch("sys.stdout", new=output), patch("app.main.build_compact_general_question_prompt") as builder:
            ask_about_project()
        self.assertIn("Verified project architecture overview", output.getvalue())
        self.assertIn("Depends on: projects\\dependency_project\\helper.py", output.getvalue())
        mock_stream.assert_not_called()
        builder.assert_not_called()


    @patch("app.main.stream_ai")
    @patch("app.main.analyze_project")
    def test_verified_semantic_architecture_bypasses_ai(
        self,
        mock_analyze,
        mock_stream,
    ):
        mock_analyze.return_value = (
            self.project_files,
            None,
        )
        question = (
            "What does each module do? "
            "Give me the verified module responsibilities."
        )
        output = io.StringIO()
        with patch(
            "builtins.input",
            side_effect=["app", question],
        ), patch(
            "sys.stdout",
            new=output,
        ), patch(
            "app.main.build_compact_general_question_prompt"
        ) as builder:
            ask_about_project()
        self.assertIn(
            "Verified semantic architecture overview",
            output.getvalue(),
        )
        self.assertIn(
            "Verified responsibility:",
            output.getvalue(),
        )
        mock_stream.assert_not_called()
        builder.assert_not_called()


    @patch("app.main.stream_ai")
    @patch("app.main.analyze_code")
    @patch("app.main.read_code_file")
    @patch("app.main.detect_language")
    def test_single_file_review_removes_unverified_ai_problems(
        self,
        mock_detect_language,
        mock_read_code_file,
        mock_analyze_code,
        mock_stream_ai,
    ):
        mock_detect_language.return_value = "Python"
        mock_read_code_file.return_value = (
            "def detect_language(filename):\n"
            "    return filename\n",
            None,
        )
        mock_analyze_code.return_value = {
            "total_lines": 2,
            "code_lines": 2,
            "blank_lines": 0,
            "syntax_valid": True,
            "syntax_error": None,
            "functions": [{"name": "detect_language", "line": 1}],
            "methods": [],
            "classes": [],
            "imports": [],
        }
        ai_response = (
            "1. What the code does:\n"
            "Detects programming languages from file extensions.\n\n"
            "2. Real problems:\n"
            "- Extensionless filenames cause AttributeError.\n"
            "- Mixed-case extensions are not handled.\n\n"
            "3. Optional improvements:\n"
            "- Add exception handling.\n"
        )
        mock_stream_ai.return_value = [ai_response]
        output = io.StringIO()
        with patch(
            "builtins.input",
            return_value=r"app\language_router.py",
        ), patch("sys.stdout", new=output):
            analyze_single_file()
        result = output.getvalue()
        self.assertIn("Detects programming languages from file extensions.", result)
        self.assertIn("2. Verified problems", result)
        self.assertIn("No verified problems found by static analysis.", result)
        self.assertNotIn("Extensionless filenames cause AttributeError", result)
        self.assertNotIn("Mixed-case extensions are not handled", result)
        self.assertNotIn("3. Optional improvements", result)
        self.assertNotIn("Add exception handling", result)
        self.assertFalse(
            result.strip().endswith(",)"),
        )
        mock_stream_ai.assert_called_once()


if __name__ == "__main__":
    unittest.main()
