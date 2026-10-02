"""Route verified scanner/analyzer explanation questions."""

from app.prompt_builder import find_mentioned_project_paths
from app.project_pipeline_presenter import format_verified_project_pipeline


VERIFIED_PIPELINE_FILES = {
    "app/project_scanner.py",
    "app/project_analyzer.py",
}


def answer_verified_project_pipeline_question(question, project_files):
    """Answer questions about the verified project pipeline."""
    normalized_question = question.casefold()
    asks_for_explanation = any(
        phrase in normalized_question
        for phrase in ("explain", "describe", "how do")
    )
    asks_about_relationship = "work together" in normalized_question
    if not (asks_for_explanation and asks_about_relationship):
        return None

    matches = find_mentioned_project_paths(question, project_files)
    normalized_paths = {
        path.replace("\\", "/").casefold()
        for path in matches
    }
    if normalized_paths != VERIFIED_PIPELINE_FILES:
        return None
    return format_verified_project_pipeline()
