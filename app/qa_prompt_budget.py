"""Conservative size guard for general project Q&A."""

MAX_GENERAL_REQUEST_CHARACTERS = 6000


def general_request_too_large(prompt, system_prompt):
    """Check the combined prompt and system-instruction size."""
    request_characters = len(prompt) + len(system_prompt)
    return request_characters > MAX_GENERAL_REQUEST_CHARACTERS
