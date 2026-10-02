from app.issue_collector import collect_project_issues
from app.context_manager import (
    MAX_PREFERRED_FILE_CHARACTERS,
    build_project_context,
)
from app.dependency_analyzer import (
    build_dependency_map,
    build_reverse_dependency_map,
    find_affected_files,
)
import json
import re


MAX_TWO_FILE_SOURCE_CHARACTERS = 6000



def build_code_review_prompt(filepath, language, content, analysis):
    analysis_text = json.dumps(
        analysis,
        indent=2,
        ensure_ascii=False,
    )

    return f"""
Review the following source file.

File: {filepath}
Language: {language}

Syntax Sage has already performed deterministic static analysis.
Treat these results as verified facts:

{analysis_text}

Review the source code using exactly these three sections:

1. What the code does
2. Real problems
3. Optional improvements

Important rules:

- Do not invent problems.
- A real problem means a bug, syntax error, likely runtime failure,
  incorrect behavior, or genuine security issue.
- Style issues, unused imports, missing docstrings, naming preferences,
  and possible enhancements are NOT real problems.
- Put those under Optional improvements instead.
- If there are no real problems, write exactly:
  "No real problems found."
- Do not say "No real problems found" if you listed a real problem.
- Do not rewrite or provide revised source code unless explicitly asked.
- Do not provide replacement code in the Optional improvements section.
- Do not add features that were not requested.
- Prefer the simplest interpretation of the code's apparent purpose.
- Use verified function, method, class, syntax, and line-number information
  when it helps the explanation.
- If you are uncertain whether something is actually a defect,
  classify it as an optional improvement rather than a real problem.


Source code:

{content}
""".strip()

def build_project_review_prompt(project_path, project_files):
    context = build_project_context(project_files)
    verified_issues = collect_project_issues(project_files)
    dependency_map = build_dependency_map(project_files)
    reverse_dependency_map = build_reverse_dependency_map(
        dependency_map
    )

    change_impact_map = {}

    for path in reverse_dependency_map:
        affected_files = find_affected_files(
            path,
            reverse_dependency_map,
        )

        if affected_files:
            change_impact_map[path] = affected_files

    verified_issues_text = json.dumps(
        verified_issues,
        indent=2,
        ensure_ascii=False,
    )

    dependency_text = json.dumps(
      {
        "depends_on": dependency_map,
        "used_by": reverse_dependency_map,
      },
      indent=2,
      ensure_ascii=False,
  )

    change_impact_text = json.dumps(
        change_impact_map,
        indent=2,
        ensure_ascii=False,
    )

    project_inventory = []

    for file_info in project_files:
        inventory_item = {
            "path": file_info["path"],
            "language": file_info["language"],
        }

        if "analysis" in file_info:
            inventory_item["analysis"] = file_info["analysis"]

        if "error" in file_info:
            inventory_item["error"] = file_info["error"]

        project_inventory.append(inventory_item)

    inventory_text = json.dumps(
        project_inventory,
        indent=2,
        ensure_ascii=False,
    )

    context_text = json.dumps(
        context,
        indent=2,
        ensure_ascii=False,
    )

    return f"""

VERIFIED ISSUES

The following issues were detected deterministically by Syntax Sage.
Treat them as verified facts.

{verified_issues_text}

VERIFIED PROJECT DEPENDENCIES

The following dependency relationships were detected deterministically by
Syntax Sage. Treat them as verified facts.

{dependency_text}

VERIFIED CHANGE IMPACT

The following potential cross-file impacts were calculated deterministically
from verified local dependency relationships.

These relationships mean that changing a listed source file may require
reviewing the affected files. They do not prove that a defect exists.

{change_impact_text}

Review the following software project.

Project: {project_path}

COMPLETE PROJECT INVENTORY

The following inventory contains every supported source file discovered by
Syntax Sage. Treat the filenames, languages, and static-analysis results as
verified facts.

{inventory_text}

SELECTED SOURCE CONTEXT

The following context contains source code selected for AI review.
Some files may be trimmed or omitted because of context limits.

{context_text}

Provide exactly these sections:

5. Real problems
6. Optional improvements

Strict rules:

- Verified change-impact relationships describe dependency risk, not defects.
- Never classify a file as defective merely because another file depends on it.
- "Potentially affects" means the dependent file may need review after a change.
- Do not claim that a change definitely breaks an affected file unless supplied
  source code or verified analysis proves it.

- The COMPLETE PROJECT INVENTORY is authoritative for which files and
  programming languages exist.
- Never invent a file or programming language that is not present in the
  complete project inventory.
- A file omitted from SELECTED SOURCE CONTEXT still exists, but its full
  source code was not reviewed by the AI.
- If a file is omitted, do not make claims about its implementation beyond
  verified static-analysis information.
- If a file is marked trimmed, do not claim to have reviewed the whole file.
- Only state facts directly supported by source code or verified analysis.
- Never infer the purpose of the project from its folder name.
- Never infer the purpose of a file from its filename alone.
- Never infer a technology's role merely from its programming language.
- A short file is not automatically incomplete or defective.
- Never classify low line count as a problem.
- Never recommend adding features merely because an example is small.
- Do not speculate about what the project may become.
- A real problem must have specific evidence in supplied source code
  or deterministic analysis.
- If there are no real problems, section 5 must contain only:
  "No real problems found."
- Optional improvements must be directly relevant to code actually reviewed.
- If no meaningful improvements exist, write:
  "No optional improvements recommended."
- Do not rewrite source code.
- Do not provide replacement code unless explicitly requested.
- If there is not enough evidence to determine something, write:
  "Not enough information to determine."
- Do not repeat the project overview, language list, file inventory,
  or function/class/method inventory. Those are generated deterministically
  by Syntax Sage.
- Verified issues are authoritative.
- Do not contradict a verified issue.
- If verified ERROR issues exist, explain them clearly in section 5.
- Do not automatically place WARNING or INFO findings in section 5.
- Do not invent additional problems unless there is direct evidence in the supplied source code.
- If there are no ERROR findings and no other directly supported defect exists,
  section 5 must contain only:
  "No real problems found."
- Do not repeat the fix for a real problem under Optional improvements.
- Required fixes belong only in Real problems.
- Optional improvements must be genuinely optional and unrelated to fixing a verified defect.
- If there are no genuine optional improvements, section 6 must contain only:
  "No optional improvements recommended."
- In section 6, never write "No real problems found."
- Severity meanings are strict:
  - ERROR = confirmed real problem.
  - WARNING = potential quality concern, not necessarily a defect.
  - INFO = neutral informational observation, never a real problem.
- Never list an INFO finding in section 5, Real problems.
- Do not convert informational findings into defects.
- WARNING findings may be mentioned only when clearly relevant, and must not be described as confirmed errors.
- Section 5 should contain verified ERROR findings and other directly proven defects only.
- If there are no ERROR findings and no other directly proven defects, section 5 must contain only:
  "No real problems found."
""".strip()


def find_mentioned_project_paths(question, project_files):
    """Identify project files explicitly mentioned in a question."""

    normalized_question = (
        question.replace("\\", "/").casefold()
    )

    normalized_files = [
        (
            file_info["path"],
            file_info["path"].replace("\\", "/").casefold(),
        )
        for file_info in project_files
    ]

    def is_mentioned(name):
        pattern = (
            r"(?<![\w.])"
            + re.escape(name)
            + r"(?![\w.])"
        )

        return re.search(
            pattern,
            normalized_question,
        ) is not None

    # Prefer an explicitly mentioned project path.
    exact_matches = [
        original
        for original, normalized in normalized_files
        if is_mentioned(normalized)
    ]

    if exact_matches:
        return exact_matches

    # Otherwise match filenames.
    # Include every match if filenames are ambiguous.
    return [
        original
        for original, normalized in normalized_files
        if is_mentioned(normalized.rsplit("/", 1)[-1])
    ]


def build_focused_file_question_prompt(
    question,
    project_files,
):
    """Build a compact prompt for one explicitly named file."""

    matches = find_mentioned_project_paths(
        question,
        project_files,
    )

    # Ambiguous or general questions need a different path.
    if len(matches) != 1:
        return None

    target = matches[0]

    file_info = next(
        item
        for item in project_files
        if item["path"] == target
    )

    source = file_info.get("content")

    if not isinstance(source, str):
        return None

    if len(source) > MAX_PREFERRED_FILE_CHARACTERS:
        return None

    return (
        "Answer the user's question using the supplied "
        "source code.\n"
        "Explain the actual implementation.\n"
        "Do not perform a code review unless requested.\n"
        "Do not suggest improvements unless requested.\n"
        "Do not invent behavior or return values.\n"
        "Do not introduce hypothetical examples, files, "
        "modules, or imports unless the user asks for examples.\n"
        "Only name files or symbols supported by the "
        "provided source or verified project evidence.\n"
        "Distinguish known dependency relationships from "
        "possible consequences of a change.\n"
        "Use 'could affect' or 'may require review'; "
        "do not claim dependent files will break.\n"
        "When explaining affected-file traversal, explicitly "
        "describe whether the target itself is included "
        "in the returned list, using the supplied code.\n"
        "Answer only the requested topics. "
        "Do not add an unsolicited code review.\n"
        "If something cannot be established from the "
        "source, identify what is missing.\n\n"
        f"QUESTION:\n{question}\n\n"
        f"SOURCE FILE:\n{target}\n\n"
        f"SOURCE:\n{source}\n"
    )


def build_focused_two_file_question_prompt(
    question,
    project_files,
):
    """Build a compact prompt for two explicitly named files."""
    matches = find_mentioned_project_paths(question, project_files)
    if len(matches) != 2:
        return None

    # A single ambiguous filename must not become a two-file question.
    basenames = {
        path.replace("\\", "/").rsplit("/", 1)[-1].casefold()
        for path in matches
    }
    if len(basenames) != 2:
        return None

    files_by_path = {item["path"]: item for item in project_files}
    sections = []
    total_source = 0
    for path in matches:
        source = files_by_path[path].get("content")
        if not isinstance(source, str):
            return None
        if len(source) > MAX_PREFERRED_FILE_CHARACTERS:
            return None
        total_source += len(source)
        if total_source > MAX_TWO_FILE_SOURCE_CHARACTERS:
            return None
        sections.append(f"SOURCE FILE:\n{path}\n\nSOURCE:\n{source}\n")

    return (
        "Answer the user's question using only the two complete source files below.\n"
        "Explain their actual implementation and how they interact.\n"
        "Distinguish returned errors from exceptions that are not caught.\n"
        "Do not invent behavior, return values, files, or exception handling.\n"
        "Do not provide examples, code, improvements, or a code review unless requested.\n"
        "If a detail cannot be established from this source, identify what is missing.\n\n"
        f"QUESTION:\n{question}\n\n"
        + "\n".join(sections)
    )


def build_project_question_prompt(
    project_path,
    project_files,
    question,
):
    preferred_paths = find_mentioned_project_paths(
        question,
        project_files,
    )

    context = build_project_context(
        project_files,
        preferred_paths=preferred_paths,
    )
    source_only_context = {
        **context,
        "files": [
            {
                key: value
                for key, value in file_info.items()
                if key != "analysis"
            }
            for file_info in context["files"]
        ],
    }
    verified_issues = collect_project_issues(project_files)

    dependency_map = build_dependency_map(project_files)
    reverse_dependency_map = build_reverse_dependency_map(
        dependency_map
    )

    change_impact_map = {}

    for path in reverse_dependency_map:
        affected_files = find_affected_files(
            path,
            reverse_dependency_map,
        )

        if affected_files:
            change_impact_map[path] = affected_files

    project_inventory = []

    for file_info in project_files:
        inventory_item = {
            "path": file_info["path"],
            "language": file_info["language"],
        }

        if "analysis" in file_info:
            inventory_item["analysis"] = file_info["analysis"]

        if "error" in file_info:
            inventory_item["error"] = file_info["error"]

        project_inventory.append(inventory_item)

    inventory_text = json.dumps(
        project_inventory,
        indent=2,
        ensure_ascii=False,
    )

    issues_text = json.dumps(
        verified_issues,
        indent=2,
        ensure_ascii=False,
    )

    dependency_text = json.dumps(
        {
            "depends_on": dependency_map,
            "used_by": reverse_dependency_map,
        },
        indent=2,
        ensure_ascii=False,
    )

    change_impact_text = json.dumps(
        change_impact_map,
        indent=2,
        ensure_ascii=False,
    )

    context_text = json.dumps(
        source_only_context,
        indent=2,
        ensure_ascii=False,
    )

    return f"""
You are Syntax Sage, a programming assistant answering a question about
an analyzed software project.

USER QUESTION

{question}

PROJECT

{project_path}

COMPLETE PROJECT INVENTORY

{inventory_text}

VERIFIED ISSUES

{issues_text}

VERIFIED PROJECT DEPENDENCIES

{dependency_text}

VERIFIED CHANGE IMPACT

{change_impact_text}

SELECTED SOURCE CONTEXT

{context_text}

Answer the user's question directly.

QUESTION-SPECIFIC RESPONSE CONTRACT

- For a factual question, answer the requested fact.
- For a dependency or change-impact question, explicitly state the verified
  dependency or affected-file relationship.
- For a "what is broken?" question, report only confirmed defects.
- For an improvement question, optional suggestions are allowed.
- For a request for code, code may be provided.
- Do not expand into other categories the user did not ask about.

Strict rules:

- Answer the user's actual question directly.
- Do not turn every question into a general code review.
- Do not automatically produce sections such as "What the code does",
  "Real problems", or "Optional improvements" unless the user's question
  specifically calls for that structure.
- Use only information supported by the supplied project data.
- Never invent files, functions, classes, methods, imports, dependencies,
  errors, APIs, runtime failures, or project behavior.
- Treat deterministic analysis as verified fact.
- Distinguish verified facts from reasonable interpretation.
- INFO findings are informational observations, not defects.
- WARNING findings are potential concerns, not confirmed defects.
- ERROR findings are confirmed problems.
- Never describe an INFO or WARNING finding as something broken.
- Never invent a runtime error based only on an assumed input type.
- Do not claim that a function rejects an input unless supplied source code
  or verified analysis proves that behavior.
- Dependency relationships do not prove that a defect exists.
- Change-impact relationships mean affected files may need review after a
  change; they do not prove those files will break.
- Change-impact language must preserve uncertainty.
- Use phrases such as "could affect", "may affect", or "may require review".
- Never say a change "will affect", "will break", or "definitely affects"
  another file unless supplied source code or verified analysis directly proves
  that outcome.
- If the user asks what could be affected by changing a file, explicitly
  answer from VERIFIED CHANGE IMPACT, name the affected files, and describe
  the relationship using uncertain language such as "could affect".
- If VERIFIED CHANGE IMPACT contains no affected files for the requested
  file, say that no affected project files were identified.
- If the user asks whether anything is broken, discuss only confirmed ERROR
  findings or defects directly proven by supplied source code.
- If there are no confirmed ERROR findings and no directly proven defects,
  say:
  "No confirmed real problems found."
- When answering whether anything is broken, do not add optional
  improvements unless the user explicitly asks for improvements.
- Do not recommend docstrings, type hints, naming changes, refactoring,
  defensive checks, validation, or new features unless the user asks for
  improvements.
- Do not provide source code, replacement code, patches, or code examples
  unless the user explicitly asks for code.
- If the answer cannot be determined from the supplied information, say:
  "Not enough information to determine."
- If source code was omitted or trimmed, acknowledge that limitation when
  relevant.
- Do not claim to have reviewed source code that was omitted.
- Keep the answer focused and concise.
""".strip()


def build_compact_general_question_prompt(
    project_path,
    project_files,
    question,
):
    """Build a compact project-wide Q&A prompt without source code."""
    verified_languages = sorted(
        {
            file_info["language"]
            for file_info in project_files
        }
    )
    lines = [
        "Use only the verified project summary below.",
        "No code review unless requested.",
        "Do not invent details absent from the summary.",
        "",
        f"QUESTION: {question}",
        "",
        f"PROJECT: {project_path}",
        f"VERIFIED FILE COUNT: {len(project_files)}",
        (
            "VERIFIED LANGUAGES: "
            + ", ".join(verified_languages)
        ),
        "Use VERIFIED FILE COUNT and VERIFIED LANGUAGES exactly.",
        "",
        "PROJECT FILES:",
    ]

    def symbol_name(symbol):
        if isinstance(symbol, str):
            return symbol
        name = symbol["name"]
        if "class" in symbol:
            return f"{symbol['class']}.{name}"
        return name

    for file_info in project_files:
        analysis = file_info.get("analysis", {})
        summary_parts = [
            f"path={file_info['path']}",
            f"language={file_info['language']}",
        ]
        if "syntax_valid" in analysis:
            summary_parts.append(f"syntax_valid={analysis['syntax_valid']}")

        for category in ("functions", "classes", "methods"):
            symbols = analysis.get(category, [])
            if symbols:
                summary_parts.append(
                    category + "=" + ",".join(symbol_name(item) for item in symbols)
                )

        if "error" in file_info:
            summary_parts.append(f"file_error={file_info['error']}")

        lines.append("- " + " | ".join(summary_parts))

    return "\n".join(lines)
