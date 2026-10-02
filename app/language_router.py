from pathlib import Path


EXTENSION_MAP = {
    ".py": "Python",
    ".java": "Java",
    ".cpp": "C++",
    ".cc": "C++",
    ".cxx": "C++",
    ".hpp": "C++",
    ".rb": "Ruby",
    ".js": "JavaScript",
    ".mjs": "JavaScript",
    ".cjs": "JavaScript",
    ".cs": "C#",
    ".php": "PHP",
    ".swift": "Swift",
    ".r": "R",
    ".sql": "SQL",
}


def detect_language(filename):
    extension = Path(filename).suffix.lower()

    return EXTENSION_MAP.get(extension, "Unknown")


if __name__ == "__main__":
    test_files = [
        "main.py",
        "Application.java",
        "engine.cpp",
        "server.js",
        "Program.cs",
        "website.php",
        "analysis.R",
        "database.sql",
        "app.swift",
        "script.rb",
        "photo.jpg",
    ]

    for filename in test_files:
        language = detect_language(filename)
        print(f"{filename:<20} -> {language}")