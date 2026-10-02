import ast


def analyze_code(content, language=None):
    lines = content.splitlines()

    total_lines = len(lines)
    blank_lines = sum(1 for line in lines if not line.strip())
    code_lines = total_lines - blank_lines

    result = {
        "total_lines": total_lines,
        "blank_lines": blank_lines,
        "code_lines": code_lines,
    }

    if language == "Python":
        result.update(analyze_python_structure(content))

    return result


def analyze_python_structure(content):
    try:
        tree = ast.parse(content)

    except SyntaxError as error:
        return {
            "syntax_valid": False,
            "syntax_error": f"Line {error.lineno}: {error.msg}",
            "functions": [],
            "methods": [],
            "classes": [],
            "imports": [],
        }

    functions = []
    methods = []
    classes = []
    imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append(
                {
                    "name": node.name,
                    "line": node.lineno,
                }
            )

            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    parameters = [arg.arg for arg in child.args.args]

                    methods.append(
                        {
                            "name": child.name,
                            "line": child.lineno,
                            "parameters": parameters,
                            "class": node.name,
                        }
                    )

        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            parent_is_class = any(
                isinstance(parent, ast.ClassDef)
                and node in parent.body
                for parent in ast.walk(tree)
            )

            if not parent_is_class:
                parameters = [arg.arg for arg in node.args.args]

                functions.append(
                    {
                        "name": node.name,
                        "line": node.lineno,
                        "parameters": parameters,
                    }
                )

        elif isinstance(node, ast.Import):
            for name in node.names:
                imports.append(name.name)

        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            imports.append(module)

    return {
        "syntax_valid": True,
        "syntax_error": None,
        "functions": functions,
        "methods": methods,
        "classes": classes,
        "imports": imports,
    }