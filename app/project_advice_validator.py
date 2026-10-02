"""Conservative validation of test-absence advice, not a coverage analyzer."""

import ast
import re


_TEST_NOUN = r"(?:unit\s+|automated\s+|integration\s+|regression\s+)?tests?"
_ABSENCE = re.compile(
    rf"\b(?:no|without|lacks?|lacking|missing)\s+(?:any\s+)?{_TEST_NOUN}\b"
    rf"|\b(?:not|never)\s+(?:been\s+)?tested\b"
    rf"|\buntested\b"
    rf"|\b{_TEST_NOUN}\s+(?:are|is)\s+(?:missing|absent|nonexistent)\b"
    rf"|\b(?:does\s+not|doesn't|do\s+not|don't)\s+have\s+(?:any\s+)?{_TEST_NOUN}\b"
    rf"|\b{_TEST_NOUN}\s+(?:do\s+not|don't|does\s+not|doesn't)\s+exist\b"
    rf"|\b(?:no|missing|lacks?)\s+test\s+coverage\b",
    re.IGNORECASE,
)
_SCOPED_OBSERVATION = (
    "No test files were identified in the supplied project inventory."
)


def _has_test_evidence(project_files):
    """Recognize filenames and Python test definitions, even in omitted files."""
    for file_info in project_files:
        path = str(file_info.get("path", "")).replace("\\", "/").lower()
        filename = path.rsplit("/", 1)[-1]
        if (
            filename.startswith("test_")
            or filename.endswith("_test.py")
            or re.search(r"\.(?:test|spec)\.[^.]+$", filename)
        ):
            return True

        content = file_info.get("content")
        if not isinstance(content, str) or file_info.get("language") != "Python":
            continue
        try:
            tree = ast.parse(content)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name.startswith("test_"):
                    return True
            if isinstance(node, ast.ClassDef):
                if any(
                    isinstance(base, ast.Name) and base.id == "TestCase"
                    or isinstance(base, ast.Attribute) and base.attr == "TestCase"
                    for base in node.bases
                ):
                    return True
    return False


def _advice_items(content):
    """Keep each bullet with its continuation paragraphs and code fences."""
    lines = content.splitlines()
    has_bullets = any(re.match(r"^(?:[-*+] |\d+[.)] )", line) for line in lines)
    items = []
    current = []
    fenced = False
    for line in lines:
        starts_item = not fenced and (
            re.match(r"^(?:[-*+] |\d+[.)] )", line)
            or line.startswith("### ")
        )
        if starts_item or (not has_bullets and not fenced and not line.strip()):
            if current:
                items.append("\n".join(current).strip())
                current = []
        current.append(line)
        if line.lstrip().startswith(("```", "~~~")):
            fenced = not fenced
    if current:
        items.append("\n".join(current).strip())
    return [item for item in items if item]


def validate_test_advice(ai_response, project_files):
    """Filter Section 6 only; absence of recognized tests is not proof of no tests.

    Test discovery conventions are incomplete. Only the exact scoped inventory
    observation is allowed without recognized evidence; categorical claims about
    a function's coverage are removed even when no test files were discovered.
    """
    heading = re.search(
        r"(?im)^[ \t]*(?:\#{1,6}[ \t]*)?(?:\*\*)?6\.\s*"
        r"Optional improvements(?:\*\*)?[ \t]*:?[ \t]*$",
        ai_response,
    )
    if heading is None:
        return ai_response

    content_start = heading.end()
    following = re.search(
        r"(?m)^[ \t]*(?:\#{1,6}[ \t]*)?(?:\*\*)?[7-9]\.\s+",
        ai_response[content_start:],
    )
    content_end = content_start + following.start() if following else len(ai_response)
    content = ai_response[content_start:content_end]
    has_tests = _has_test_evidence(project_files)
    kept = []
    removed = False
    for item in _advice_items(content):
        plain = re.sub(r"[`*_]", "", item)
        plain = re.sub(r"\s+", " ", plain).strip()
        scoped = re.sub(r"^(?:[-+] |\d+[.)] )", "", plain)
        if _ABSENCE.search(plain) and not (
            scoped == _SCOPED_OBSERVATION and not has_tests
        ):
            removed = True
            continue
        kept.append(item)
    if not removed:
        return ai_response
    validated = "\n\n".join(kept) or "No optional improvements recommended."
    suffix = ai_response[content_end:]
    return ai_response[:content_start] + "\n\n" + validated + ("\n\n" + suffix if suffix else "")


def filter_false_direct_print_advice(ai_response, project_files):
    """
    Remove unsupported claims that a function prints results
    directly when verified source shows it returns results
    without calling print().
    """

    def function_returns_without_print(function_name):
        matching_functions = []

        for file_info in project_files:
            if file_info.get("language") != "Python":
                continue

            content = file_info.get("content")

            if not isinstance(content, str):
                continue

            try:
                tree = ast.parse(content)
            except SyntaxError:
                continue

            for node in tree.body:
                if isinstance(
                    node,
                    (ast.FunctionDef, ast.AsyncFunctionDef),
                ) and node.name == function_name:
                    matching_functions.append(node)

        # Ambiguous or unavailable evidence is not proof.
        if len(matching_functions) != 1:
            return False

        function = matching_functions[0]

        has_return = any(
            isinstance(node, ast.Return)
            for node in ast.walk(function)
        )

        has_print = any(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "print"
            for node in ast.walk(function)
        )

        return has_return and not has_print

    cleaned_lines = []

    for line in ai_response.splitlines():
        # Only examine advice bullets that specifically claim
        # a named function prints results directly.
        if re.match(r"^\s*[-*]\s+", line):
            match = re.search(
                r"`([A-Za-z_]\w*)`\s+function\b"
                r".*?\bprints?\b.*?\bdirectly\b",
                line,
                flags=re.IGNORECASE,
            )

            if match:
                function_name = match.group(1)

                if function_returns_without_print(function_name):
                    continue

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()
