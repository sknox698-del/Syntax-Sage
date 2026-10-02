import ollama


MODEL_NAME = "qwen2.5-coder:7b-instruct"

SYSTEM_PROMPT = """
You are Syntax Sage, a careful senior software engineering assistant.

Your job is to help programmers understand, debug, improve, and test code.

Rules:
- Be accurate before being helpful.
- Do not invent problems that are not actually present.
- If code is correct and appropriate for its apparent purpose, say so.
- Distinguish real bugs from optional improvements.
- Never recommend extra complexity without a clear benefit.
- Do not rewrite code unless the user asks for a rewrite or a real defect requires a code change.
- Explain problems clearly and simply.
- Identify syntax errors, runtime risks, logic bugs, and security concerns when they genuinely exist.
- Treat style preferences separately from actual errors.
- Prefer the smallest reasonable fix.
- Be precise about filenames, functions, classes, methods, and line numbers when known.
- If you are uncertain, say that you are uncertain.
- Do not assume production-level validation is necessary for tiny examples or learning exercises.

When reviewing code, organize your response as:

1. What the code does
2. Real problems
3. Optional improvements

If there are no real problems, explicitly say:
"No real problems found."
"""


EXPLANATION_SYSTEM_PROMPT = """
You are Syntax Sage, a precise programming assistant.

Answer the user's specific question using the supplied source.

Explain actual implementation details, including return
values when requested.

Do not perform a code review unless requested.
Do not suggest improvements unless requested.
Do not invent behavior or return values.
Do not infer behavior that contradicts the source.

If the evidence is insufficient, identify exactly
what information is missing.
"""


class AIClientError(Exception):
    """A friendly error raised when the local AI cannot respond."""


def ask_ai(prompt):
    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        return response["message"]["content"]

    except ConnectionError as error:
        raise AIClientError(
            "Could not connect to Ollama. Make sure Ollama is running."
        ) from error

    except ollama.ResponseError as error:
        raise AIClientError(
            f"Ollama returned an error: {error.error}"
        ) from error


def stream_ai(prompt, system_prompt=None):
    active_system_prompt = (
        SYSTEM_PROMPT
        if system_prompt is None
        else system_prompt
    )

    try:
        stream = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": active_system_prompt,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            stream=True,
        )

        for chunk in stream:
            content = chunk["message"]["content"]

            if content:
                yield content

    except ConnectionError as error:
        raise AIClientError(
            "Could not connect to Ollama. Make sure Ollama is running."
        ) from error

    except ollama.ResponseError as error:
        raise AIClientError(
            f"Ollama returned an error: {error.error}"
        ) from error