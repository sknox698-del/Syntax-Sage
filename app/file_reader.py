from pathlib import Path


def read_code_file(filepath):
    path = Path(filepath)

    if not path.exists():
        return None, "File not found."

    if not path.is_file():
        return None, "The path is not a file."

    try:
        content = path.read_text(encoding="utf-8")
        return content, None

    except UnicodeDecodeError:
        return None, "The file is not a readable UTF-8 text file."

    except OSError as error:
        return None, f"Could not read file: {error}"