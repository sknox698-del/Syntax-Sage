def _module_names_for_path(path):
    normalized_path = str(path).replace("\\", "/")

    if not normalized_path.lower().endswith(".py"):
        return set()

    without_extension = normalized_path[:-3]

    parts = [
        part
        for part in without_extension.split("/")
        if part not in ("", ".")
    ]

    if parts and parts[-1] == "__init__":
        parts = parts[:-1]

    module_names = set()

    for index in range(len(parts)):
        module_name = ".".join(parts[index:])

        if module_name:
            module_names.add(module_name)

    return module_names


def _resolve_local_import(
    imported_module,
    module_lookup,
    source_path,
):
    normalized_import = imported_module.lstrip(".")

    if not normalized_import:
        return None

    parts = normalized_import.split(".")

    for end_index in range(len(parts), 0, -1):
        candidate = ".".join(parts[:end_index])

        matching_paths = [
            path
            for path in module_lookup.get(candidate, [])
            if path != source_path
        ]

        if len(matching_paths) == 1:
            return matching_paths[0]

        if len(matching_paths) > 1:
            # Ambiguous local module name.
            # Do not guess.
            return None

    return None


def build_dependency_map(project_files):
    module_lookup = {}

    for file_info in project_files:
        if file_info["language"] != "Python":
            continue

        path = file_info["path"]

        for module_name in _module_names_for_path(path):
            module_lookup.setdefault(
                module_name,
                [],
            ).append(path)

    dependency_map = {}

    for file_info in project_files:
        path = file_info["path"]

        if file_info["language"] != "Python":
            continue

        analysis = file_info.get("analysis", {})
        imports = analysis.get("imports", [])

        local_dependencies = []

        for imported_module in imports:
            dependency_path = _resolve_local_import(
                imported_module,
                module_lookup,
                path,
            )

            if dependency_path is not None:
                local_dependencies.append(
                    dependency_path
                )

        dependency_map[path] = sorted(
            set(local_dependencies)
        )

    return dependency_map


def build_reverse_dependency_map(dependency_map):
    reverse_map = {
        path: []
        for path in dependency_map
    }

    for source_path, dependencies in dependency_map.items():
        for dependency_path in dependencies:
            if dependency_path not in reverse_map:
                reverse_map[dependency_path] = []

            reverse_map[dependency_path].append(source_path)

    for path in reverse_map:
        reverse_map[path] = sorted(set(reverse_map[path]))

    return reverse_map

def find_affected_files(target_path, reverse_dependency_map):
    affected = set()
    pending = list(
        reverse_dependency_map.get(target_path, [])
    )

    while pending:
        current_path = pending.pop(0)

        if current_path in affected:
            continue

        affected.add(current_path)

        for dependent in reverse_dependency_map.get(
            current_path,
            [],
        ):
            if dependent not in affected:
                pending.append(dependent)

    affected.discard(target_path)

    return sorted(affected)


def get_change_impact(target_path, project_files):
    dependency_map = build_dependency_map(project_files)
    reverse_dependency_map = build_reverse_dependency_map(
        dependency_map
    )

    if target_path not in reverse_dependency_map:
        return {
            "found": False,
            "target": target_path,
            "affected_files": [],
        }

    affected_files = find_affected_files(
        target_path,
        reverse_dependency_map,
    )

    return {
        "found": True,
        "target": target_path,
        "affected_files": affected_files,
    }
