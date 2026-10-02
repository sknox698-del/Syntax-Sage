import json
import unittest

from app.prompt_builder import (
    build_compact_general_question_prompt,
    build_focused_two_file_question_prompt,
    build_focused_file_question_prompt,
    build_project_question_prompt,
    find_mentioned_project_paths,
)


class TestProjectQuestionPrompt(unittest.TestCase):

    def setUp(self):
        self.project_files = [
            {
                "path": "project/main.py",
                "language": "Python",
                "content": "import helper\n\nprint(helper.greet('Steve'))",
                "analysis": {
                    "total_lines": 3,
                    "code_lines": 2,
                    "blank_lines": 1,
                    "syntax_valid": True,
                    "imports": ["helper"],
                    "functions": [],
                    "classes": [],
                    "methods": [],
                },
            },
            {
                "path": "project/helper.py",
                "language": "Python",
                "content": (
                    "def greet(name):\n"
                    "    return f'Hello, {name}'"
                ),
                "analysis": {
                    "total_lines": 2,
                    "code_lines": 2,
                    "blank_lines": 0,
                    "syntax_valid": True,
                    "imports": [],
                    "functions": [
                        {
                            "name": "greet",
                            "line": 1,
                        },
                    ],
                    "classes": [],
                    "methods": [],
                },
            },
        ]

    def test_question_prompt_does_not_duplicate_analysis(self):
        target = self.project_files[1]
        marker = "UNIQUE_QA_ANALYSIS_MARKER"
        target["analysis"]["qa_marker"] = marker

        prompt = build_project_question_prompt(
            "project",
            self.project_files,
            "Explain helper.py",
        )

        self.assertEqual(prompt.count(marker), 1)

        inventory, _ = json.JSONDecoder().raw_decode(
            prompt.split("\nCOMPLETE PROJECT INVENTORY\n", 1)[1].lstrip()
        )
        inventory_target = next(
            item for item in inventory
            if item["path"] == target["path"]
        )
        self.assertEqual(inventory_target["analysis"], target["analysis"])

        context, _ = json.JSONDecoder().raw_decode(
            prompt.split("\nSELECTED SOURCE CONTEXT\n", 1)[1].lstrip()
        )
        selected = next(
            item for item in context["files"]
            if item["path"] == target["path"]
        )
        self.assertEqual(selected["content"], target["content"])
        self.assertEqual(selected["language"], target["language"])
        self.assertFalse(selected["trimmed"])
        for item in context["files"]:
            self.assertNotIn("analysis", item)

    def test_question_prompt_contains_user_question(self):
        prompt = build_project_question_prompt(
            "project",
            self.project_files,
            "What does helper.py do?",
        )

        self.assertIn(
            "What does helper.py do?",
            prompt,
        )

        self.assertIn(
            "USER QUESTION",
            prompt,
        )

    def test_question_prompt_contains_project_inventory(self):
        prompt = build_project_question_prompt(
            "project",
            self.project_files,
            "What files are in this project?",
        )

        self.assertIn(
            "COMPLETE PROJECT INVENTORY",
            prompt,
        )

        self.assertIn(
            "project/main.py",
            prompt,
        )

        self.assertIn(
            "project/helper.py",
            prompt,
        )

        self.assertIn(
            '"name": "greet"',
            prompt,
        )

    def test_question_prompt_contains_verified_dependencies(self):
        prompt = build_project_question_prompt(
            "project",
            self.project_files,
            "What depends on helper.py?",
        )

        self.assertIn(
            "VERIFIED PROJECT DEPENDENCIES",
            prompt,
        )

        self.assertIn(
            '"depends_on"',
            prompt,
        )

        self.assertIn(
            '"used_by"',
            prompt,
        )

        self.assertIn(
            "project/main.py",
            prompt,
        )

        self.assertIn(
            "project/helper.py",
            prompt,
        )

    def test_question_prompt_contains_change_impact(self):
        prompt = build_project_question_prompt(
            "project",
            self.project_files,
            "What could be affected if helper.py changes?",
        )

        self.assertIn(
            "VERIFIED CHANGE IMPACT",
            prompt,
        )

        self.assertIn(
            '"project/helper.py"',
            prompt,
        )

        self.assertIn(
            '"project/main.py"',
            prompt,
        )

    def test_question_prompt_contains_grounding_rules(self):
        prompt = build_project_question_prompt(
            "project",
            self.project_files,
            "Is anything broken?",
        )

        self.assertIn(
            "INFO findings are informational observations, not defects.",
            prompt,
        )

        self.assertIn(
            "Dependency relationships do not prove that a defect exists.",
            prompt,
        )

        self.assertIn(
            "Not enough information to determine.",
            prompt,
        )


    def test_question_prompt_requires_explicit_change_impact_answer(self):
        prompt = build_project_question_prompt(
            "project",
            self.project_files,
            "What could be affected if helper.py changes?",
        )

        self.assertIn(
            "If the user asks what could be affected by changing a file, explicitly",
            prompt,
        )

        self.assertIn(
            "answer from VERIFIED CHANGE IMPACT, name the affected files, and describe",
            prompt,
        )

        self.assertIn(
            '"project/helper.py"',
            prompt,
        )

        self.assertIn(
            '"project/main.py"',
            prompt,
        )


    def test_question_prompt_forbids_invented_runtime_errors(self):
        prompt = build_project_question_prompt(
            "project",
            self.project_files,
            "Is anything broken?",
        )

        self.assertIn(
            "Never invent a runtime error based only on an assumed input type.",
            prompt,
        )

        self.assertIn(
            "Do not claim that a function rejects an input unless supplied source code",
            prompt,
        )

        self.assertIn(
            "No confirmed real problems found.",
            prompt,
        )


    def test_question_prompt_forbids_unsolicited_improvements_and_code(self):
        prompt = build_project_question_prompt(
            "project",
            self.project_files,
            "Is anything broken?",
        )

        self.assertIn(
            "do not add optional",
            prompt,
        )

        self.assertIn(
            "improvements unless the user explicitly asks for improvements.",
            prompt,
        )

        self.assertIn(
            "Do not provide source code, replacement code, patches, or code examples",
            prompt,
        )


    def test_question_prompt_requires_uncertain_change_impact_language(self):
        prompt = build_project_question_prompt(
            "project",
            self.project_files,
            "What could be affected if helper.py changes?",
        )

        self.assertIn(
            "Change-impact language must preserve uncertainty.",
            prompt,
        )

        self.assertIn(
            'Use phrases such as "could affect", "may affect", or "may require review".',
            prompt,
        )

        self.assertIn(
            'Never say a change "will affect", "will break", or "definitely affects"',
            prompt,
        )

    def test_detects_explicit_windows_project_path(self):
        files = [
            {
                "path": "app\\dependency_analyzer.py",
                "language": "Python",
            },
            {
                "path": "app\\main.py",
                "language": "Python",
            },
        ]

        result = find_mentioned_project_paths(
            "Explain APP/dependency_analyzer.py",
            files,
        )

        self.assertEqual(
            result,
            ["app\\dependency_analyzer.py"],
        )

    def test_ambiguous_filename_selects_all_matches(self):
        files = [
            {
                "path": "app/helper.py",
                "language": "Python",
            },
            {
                "path": "tests/helper.py",
                "language": "Python",
            },
        ]

        result = find_mentioned_project_paths(
            "What does helper.py do?",
            files,
        )

        self.assertEqual(
            result,
            ["app/helper.py", "tests/helper.py"],
        )

    def test_question_prioritizes_requested_source(self):
        def make_file(path, content):
            return {
                "path": path,
                "language": "Python",
                "content": content,
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
            }

        target_content = (
            "TARGET_START\n"
            + "D" * 3500
            + "\nTARGET_END"
        )

        files = [
            make_file("app/main.py", "M" * 4000),
            make_file(
                "app/dependency_analyzer.py",
                target_content,
            ),
        ]

        for index in range(10):
            files.append(
                make_file(
                    f"app/small_{index}.py",
                    "S" * 1000,
                )
            )

        prompt = build_project_question_prompt(
            "app",
            files,
            "Explain dependency_analyzer.py",
        )

        # The end marker proves the requested file
        # survived the context-selection limit.
        self.assertIn("TARGET_START", prompt)
        self.assertIn("TARGET_END", prompt)

    def test_focused_prompt_contains_requested_source(self):
        files = [
            {
                "path": "app/dependency_analyzer.py",
                "language": "Python",
                "content": "UNIQUE_DEPENDENCY_SOURCE_MARKER",
            },
            {
                "path": "app/main.py",
                "language": "Python",
                "content": "UNRELATED_SOURCE_MARKER",
            },
        ]

        prompt = build_focused_file_question_prompt(
            "Explain dependency_analyzer.py",
            files,
        )

        self.assertIsNotNone(prompt)
        self.assertIn(
            "UNIQUE_DEPENDENCY_SOURCE_MARKER",
            prompt,
        )
        self.assertNotIn(
            "UNRELATED_SOURCE_MARKER",
            prompt,
        )
        self.assertNotIn(
            "COMPLETE PROJECT INVENTORY",
            prompt,
        )

    def test_focused_prompt_rejects_ambiguous_filename(self):
        files = [
            {
                "path": "app/helper.py",
                "content": "APP_SOURCE",
            },
            {
                "path": "tests/helper.py",
                "content": "TEST_SOURCE",
            },
        ]

        prompt = build_focused_file_question_prompt(
            "Explain helper.py",
            files,
        )

        self.assertIsNone(prompt)


    def test_focused_prompt_preserves_target_exclusion_and_factuality_rules(self):
        source = (
            "def trace_named_dependents(target, affected):\n"
            "    affected.discard(target)\n"
            "    return sorted(affected)\n"
        )
        prompt = build_focused_file_question_prompt(
            "Explain trace_named_dependents in traversal.py",
            [{"path": "app/traversal.py", "language": "Python", "content": source}],
        )

        self.assertIsNotNone(prompt)
        self.assertEqual(prompt.split("SOURCE:\n", 1)[1], source + "\n")
        self.assertIn("affected.discard(target)", prompt)
        rules = (
            "Do not introduce hypothetical examples, files, modules, or imports unless the user asks for examples.",
            "Only name files or symbols supported by the provided source or verified project evidence.",
            "Distinguish known dependency relationships from possible consequences of a change.",
            "Use 'could affect' or 'may require review'; do not claim dependent files will break.",
            "When explaining affected-file traversal, explicitly describe whether the target itself is included in the returned list, using the supplied code.",
            "Answer only the requested topics. Do not add an unsolicited code review.",
        )
        for rule in rules:
            with self.subTest(rule=rule):
                self.assertIn(rule, prompt)


    def test_two_file_prompt_includes_only_requested_complete_sources(self):
        files = [
            {"path": "app/scanner.py", "content": "SCANNER_START\nscan()\nSCANNER_END"},
            {"path": "app/analyzer.py", "content": "ANALYZER_START\nanalyze()\nANALYZER_END"},
            {"path": "app/other.py", "content": "UNRELATED_SOURCE_MARKER"},
        ]
        for question in (
            "Explain scanner.py and analyzer.py",
            "Explain APP/SCANNER.py and app/analyzer.py",
            "Explain app\\scanner.py and app\\analyzer.py",
        ):
            with self.subTest(question=question):
                prompt = build_focused_two_file_question_prompt(question, files)
                self.assertIsNotNone(prompt)
                for item in files[:2]:
                    self.assertIn(item["path"], prompt)
                    self.assertIn(item["content"], prompt)
                self.assertNotIn("UNRELATED_SOURCE_MARKER", prompt)
                self.assertNotIn("app/other.py", prompt)
                self.assertNotIn("COMPLETE PROJECT INVENTORY", prompt)
        for question in ("Explain the project", "Explain scanner.py", "Explain scanner.py, analyzer.py and other.py"):
            with self.subTest(question=question):
                self.assertIsNone(build_focused_two_file_question_prompt(question, files))

    def test_two_file_prompt_rejects_ambiguous_basename(self):
        files = [
            {"path": "app/helper.py", "content": "APP_SOURCE"},
            {"path": "tests/helper.py", "content": "TEST_SOURCE"},
        ]
        self.assertIsNone(build_focused_two_file_question_prompt("Explain helper.py", files))

    def test_two_file_prompt_enforces_complete_source_limits(self):
        for first_size, second_size, accepted in (
            (5001, 1, False), (1, 5001, False),
            (3000, 3001, False), (5000, 1000, True),
            (3000, 3000, True),
        ):
            with self.subTest(first=first_size, second=second_size):
                files = [
                    {"path": "app/first.py", "content": "A" * first_size},
                    {"path": "app/second.py", "content": "B" * second_size},
                ]
                prompt = build_focused_two_file_question_prompt("Explain first.py and second.py", files)
                if accepted:
                    self.assertIsNotNone(prompt)
                    for item in files:
                        self.assertIn(item["content"], prompt)
                else:
                    self.assertIsNone(prompt)

    def test_two_file_prompt_rejects_unavailable_source(self):
        for index in (0, 1):
            for missing in ({}, {"content": None}, {"content": 123}):
                with self.subTest(index=index, missing=missing):
                    files = [
                        {"path": "app/first.py", "content": "FIRST_SOURCE"},
                        {"path": "app/second.py", "content": "SECOND_SOURCE"},
                    ]
                    files[index] = {"path": files[index]["path"], **missing}
                    self.assertIsNone(build_focused_two_file_question_prompt("Explain first.py and second.py", files))


    def test_compact_general_prompt_uses_summary_not_source(self):
        from app.code_analyzer import analyze_code

        source = (
            "SECRET_SOURCE_MARKER = 1\n"
            "def run():\n    pass\n"
            "class Example:\n    def execute(self):\n        pass\n"
        )
        for analysis in (
            analyze_code(source, "Python"),
            {
                "syntax_valid": True,
                "functions": ["run"],
                "classes": ["Example"],
                "methods": ["Example.execute"],
            },
        ):
            with self.subTest(analysis=analysis):
                prompt = build_compact_general_question_prompt(
                    "app",
                    [{"path": "app/example.py", "language": "Python",
                      "content": source, "analysis": analysis}],
                    "What does this project contain?",
                )
                self.assertIn("functions=run", prompt)
                self.assertIn("classes=Example", prompt)
                self.assertIn("methods=Example.execute", prompt)
                self.assertIn("syntax_valid=True", prompt)
                self.assertNotIn("SECRET_SOURCE_MARKER", prompt)
                self.assertNotIn("def run", prompt)
                self.assertEqual(prompt.count("path=app/example.py"), 1)

    def test_compact_general_prompt_lists_all_files(self):
        files = self.project_files + [
            {"path": "project/script.js", "language": "JavaScript"},
        ]
        question = "Give me an overview of this project."
        prompt = build_compact_general_question_prompt("project", files, question)
        self.assertIn(f"QUESTION: {question}", prompt)
        self.assertIn("PROJECT: project", prompt)
        for file_info in files:
            self.assertEqual(prompt.count(f"path={file_info['path']}"), 1)
            self.assertIn(f"language={file_info['language']}", prompt)

    def test_compact_general_prompt_includes_verified_aggregate_inventory(self):
        files = [
            {
                "path": "app/first.py",
                "language": "Python",
            },
            {
                "path": "app/second.py",
                "language": "Python",
            },
            {
                "path": "app/script.js",
                "language": "JavaScript",
            },
        ]
        prompt = build_compact_general_question_prompt(
            "app",
            files,
            "Summarize the inventory.",
        )
        self.assertIn(
            "VERIFIED FILE COUNT: 3",
            prompt,
        )
        self.assertIn(
            "VERIFIED LANGUAGES: JavaScript, Python",
            prompt,
        )
        self.assertIn(
            "Use VERIFIED FILE COUNT and VERIFIED LANGUAGES exactly.",
            prompt,
        )

    def test_compact_general_prompt_preserves_file_error(self):
        prompt = build_compact_general_question_prompt(
            "app",
            [{"path": "app/unreadable.py", "language": "Python",
              "error": "Permission denied"}],
            "What files are available?",
        )
        self.assertIn("path=app/unreadable.py", prompt)
        self.assertIn("file_error=Permission denied", prompt)
        self.assertNotIn("syntax_valid=", prompt)


if __name__ == "__main__":
    unittest.main()
