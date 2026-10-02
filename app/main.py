from app.project_architecture_route import answer_verified_architecture_question
from app.review_cleaner import clean_optional_improvements
from app.qa_prompt_budget import general_request_too_large
from app.ai_client import (
    AIClientError,
    EXPLANATION_SYSTEM_PROMPT,
    stream_ai,
)
from app.single_file_review_guard import (
    enforce_verified_single_file_review,
)
from app.code_analyzer import analyze_code
from app.config import APP_NAME, VERSION
from app.context_manager import build_project_context
from app.dependency_analyzer import get_change_impact
from app.dependency_explanation_route import (
    answer_verified_dependency_question,
    answer_verified_combined_dependency_question,
)
from app.file_reader import read_code_file
from app.language_router import detect_language
from app.project_answer_cleaner import clean_project_question_answer
from app.project_question_router import (
    answer_project_question_deterministically,
    classify_project_question,
)
from app.project_pipeline_route import answer_verified_project_pipeline_question
from app.project_reporter import build_project_report
from app.project_review_guard import enforce_verified_project_errors
from app.project_advice_validator import (
    validate_test_advice,
    filter_false_direct_print_advice,
)
from app.project_scanner import scan_project
from app.project_analyzer import analyze_project
from app.prompt_builder import (
    build_focused_file_question_prompt,
    build_focused_two_file_question_prompt,
    build_code_review_prompt,
    build_project_review_prompt,
    build_compact_general_question_prompt,
)

from app.semantic_architecture_route import (
    answer_verified_semantic_architecture_question,
)

def analyze_single_file():
    filepath = input("\nEnter a file to analyze: ").strip()

    language = detect_language(filepath)

    print(f"\nDetected language: {language}")

    content, error = read_code_file(filepath)

    if error:
        print(f"\nError: {error}")
        return

    analysis = analyze_code(
        content,
        language,
    )

    print("\nCode analysis:")
    print(f"Total lines: {analysis['total_lines']}")
    print(f"Code lines: {analysis['code_lines']}")
    print(f"Blank lines: {analysis['blank_lines']}")

    if language == "Python":
        print(
            f"Syntax valid: "
            f"{analysis.get('syntax_valid')}"
        )

        print("Functions:")

        functions = analysis.get("functions", [])

        if functions:
            for function in functions:
                print(
                    f"  {function['name']} "
                    f"(line {function['line']})"
                )
        else:
            print("None")

        print("Methods:")

        methods = analysis.get("methods", [])

        if methods:
            for method in methods:
                print(
                    f"  {method['class']}."
                    f"{method['name']} "
                    f"(line {method['line']})"
                )
        else:
            print("None")

        print("Classes:")

        classes = analysis.get("classes", [])

        if classes:
            for class_info in classes:
                print(
                    f"  {class_info['name']} "
                    f"(line {class_info['line']})"
                )
        else:
            print("None")

        print(
            f"Imports: "
            f"{analysis.get('imports', [])}"
        )

        if analysis.get("syntax_valid") is False:
            print(
                f"Syntax error: "
                f"{analysis.get('syntax_error')}"
            )

    print("\nFile contents:\n")
    print(content)
    print("-" * 40)

    prompt = build_code_review_prompt(
        filepath,
        language,
        content,
        analysis,
    )

    print("\nAI analysis:\n")

    try:
        response_parts = []

        for chunk in stream_ai(prompt):
            response_parts.append(chunk)

        ai_response = "".join(response_parts)

        cleaned_response = enforce_verified_single_file_review(
            ai_response,
            analysis,
        )

        print(cleaned_response)

    except AIClientError as error:
        print(f"AI error: {error}")


def scan_entire_project():
    project_path = input("Enter a project folder: ").strip()

    project_files, error = analyze_project(project_path)

    if error:
        print(f"Error: {error}")
        return

    print()
    print(f"Supported source files found: {len(project_files)}")
    print("-" * 40)

    total_lines = 0

    for file_info in project_files:
        print()
        print(f"File: {file_info['path']}")
        print(f"Language: {file_info['language']}")

        if "error" in file_info:
            print(f"Error: {file_info['error']}")
            continue

        analysis = file_info["analysis"]

        print(f"Total lines: {analysis['total_lines']}")
        print(f"Code lines: {analysis['code_lines']}")
        print(f"Blank lines: {analysis['blank_lines']}")

        total_lines += analysis["total_lines"]

        if file_info["language"] == "Python":
            print(f"Syntax valid: {analysis['syntax_valid']}")

    print()
    print("-" * 40)
    print(f"Project total lines: {total_lines}")
    print("-" * 40)

    context = build_project_context(project_files)

    print()
    print("Verified project report:")
    print("-" * 40)

    project_report = build_project_report(
        project_path=project_path,
        project_files=project_files,
        context=context,
    )

    print(project_report)
    print("-" * 40)

    print()
    print("AI context:")
    print(f"Files available: {context['files_available']}")
    print(f"Files included: {context['files_included']}")
    print(f"Characters included: {context['total_characters']}")

    print("Trimmed files:")
    if context["trimmed_files"]:
        for filepath in context["trimmed_files"]:
            print(f"  - {filepath}")
    else:
        print("  None")

    print("Omitted files:")
    if context["omitted_files"]:
        for filepath in context["omitted_files"]:
            print(f"  - {filepath}")
    else:
        print("  None")

    print()
    print("AI project review:")
    print("-" * 40)

    prompt = build_project_review_prompt(
        project_path=project_path,
        project_files=project_files,
    )

    try:
        response_parts = []

        for chunk in stream_ai(prompt):
            response_parts.append(chunk)

        ai_response = "".join(response_parts)

        guarded_response = enforce_verified_project_errors(
            ai_response,
            project_files,
        )

        validated_response = validate_test_advice(
            guarded_response,
            project_files,
        )

        validated_response = filter_false_direct_print_advice(
            validated_response,
            project_files,
        )

        print(validated_response)

    except AIClientError as error:
        print()
        print(f"AI unavailable: {error}")

    print("-" * 40)


def check_change_impact():
    project_path = input(
        "\nEnter a project folder: "
    ).strip()

    project_files, error = analyze_project(project_path)

    if error:
        print(f"\nError: {error}")
        return

    if not project_files:
        print("\nNo supported source files were found.")
        return

    print("\nAvailable project files:")

    for file_info in project_files:
        print(f"- {file_info['path']}")

    target_path = input(
        "\nEnter the file to check: "
    ).strip()

    result = get_change_impact(
        target_path,
        project_files,
    )

    print()
    print("Change impact")
    print("-" * 40)

    if not result["found"]:
        print(
            "The requested file was not found "
            "in the analyzed dependency map."
        )
        return

    print(f"Target: {result['target']}")

    affected_files = result["affected_files"]

    if not affected_files:
        print(
            "\nNo other project files are currently "
            "affected by this file."
        )
        return

    print("\nPotentially affected files:")

    for affected_path in affected_files:
        print(f"- {affected_path}")


def ask_about_project():
    project_path = input(
        "\nEnter a project folder: "
    ).strip()

    project_files, error = analyze_project(project_path)

    if error:
        print(f"\nError: {error}")
        return

    if not project_files:
        print("\nNo supported source files were found.")
        return

    print("\nAvailable project files:")

    for file_info in project_files:
        print(f"- {file_info['path']}")

    question = input(
        "\nAsk Syntax Sage about this project: "
    ).strip()

    if not question:
        print("\nA question is required.")
        return

    question_type = classify_project_question(question)

    verified_answer = (
        answer_project_question_deterministically(
            question,
            project_files,
        )
    )

    normalized_question = question.lower()

    general_markers = (
        "what does",
        "what is",
        "explain",
        "describe",
        "how does",
        "how do",
    )

    has_general_part = any(
        marker in normalized_question
        for marker in general_markers
    )

    print()
    print("Syntax Sage answer")
    print("-" * 40)

    # Recognize this narrow explanation before generic problem keywords.
    pipeline_answer = answer_verified_project_pipeline_question(
        question,
        project_files,
    )

    # Questions about confirmed problems should always use
    # deterministic project evidence.
    if question_type == "problems" and verified_answer and pipeline_answer is None:
        print(verified_answer)
        print("-" * 40)
        return

    # A pure dependency/change-impact question can also be answered
    # completely from verified project data.
    if (
        question_type == "change_impact"
        and verified_answer
        and not has_general_part
    ):
        print(verified_answer)
        print("-" * 40)
        return

    combined_explanation = answer_verified_combined_dependency_question(
        question,
        project_files,
    )
    if combined_explanation is not None:
        print(combined_explanation)
        if question_type == "change_impact" and verified_answer and has_general_part:
            print()
            print("Verified change impact:")
            print(verified_answer)
        print("-" * 40)
        return

    dependency_explanation = answer_verified_dependency_question(
        question,
        project_files,
    )
    if dependency_explanation is not None:
        print(dependency_explanation)
        print("-" * 40)
        return

    if pipeline_answer is not None:
        print(pipeline_answer)
        print("-" * 40)
        return

    semantic_architecture_answer = (
        answer_verified_semantic_architecture_question(
            question,
            project_files,
        )
    )
    if semantic_architecture_answer is not None:
        print(semantic_architecture_answer)
        print("-" * 40)
        return

    architecture_answer = answer_verified_architecture_question(
        question,
        project_files,
    )
    if architecture_answer is not None:
        print(architecture_answer)
        print("-" * 40)
        return

    # General or mixed questions still use the AI for explanation.
    focused_prompt = (
        build_focused_file_question_prompt(
            question,
            project_files,
        )
        if has_general_part
        else None
    )

    two_file_prompt = (
        build_focused_two_file_question_prompt(
            question,
            project_files,
        )
        if has_general_part and focused_prompt is None
        else None
    )

    if focused_prompt is not None:
        prompt = focused_prompt
        selected_system_prompt = EXPLANATION_SYSTEM_PROMPT
    elif two_file_prompt is not None:
        prompt = two_file_prompt
        selected_system_prompt = EXPLANATION_SYSTEM_PROMPT
    else:
        prompt = build_compact_general_question_prompt(
            project_path=project_path,
            project_files=project_files,
            question=question,
        )
        selected_system_prompt = EXPLANATION_SYSTEM_PROMPT
        if general_request_too_large(prompt, selected_system_prompt):
            print(
                "The general project prompt is too large "
                "for the current conservative Q&A limit."
            )
            print(
                "Try asking about one or two specific "
                "source files instead."
            )
            print("-" * 40)
            return

    try:
        response_parts = []

        for chunk in stream_ai(
            prompt,
            system_prompt=selected_system_prompt,
        ):
            response_parts.append(chunk)

        ai_response = "".join(response_parts)

        cleaned_response = clean_project_question_answer(
            ai_response,
            question,
        )

        if cleaned_response:
            print(cleaned_response)

    except AIClientError as error:
        print()
        print(f"AI unavailable: {error}")

    # For mixed questions, append the deterministic result so the
    # verified dependency/change-impact information cannot be omitted
    # or rewritten with stronger certainty.
    if (
        question_type == "change_impact"
        and verified_answer
        and has_general_part
    ):
        print()
        print("Verified change impact:")
        print(verified_answer)

    print("-" * 40)


def main():
    print(f"{APP_NAME} v{VERSION}")
    print("Programming AI starting...")

    while True:
        print()
        print("1. Analyze one file")
        print("2. Scan an entire project")
        print("3. Check change impact")
        print("4. Ask Syntax Sage about a project")
        print("5. Exit")

        choice = input("\nChoose an option: ").strip()

        if choice == "1":
            analyze_single_file()

        elif choice == "2":
            scan_entire_project()

        elif choice == "3":
            check_change_impact()

        elif choice == "4":
            ask_about_project()

        elif choice == "5":
            print("\nSyntax Sage shutting down.")
            break

        else:
            print(
                "\nInvalid choice. "
                "Please choose 1, 2, 3, 4, or 5."
            )


if __name__ == "__main__":
    main()
