from pathlib import Path


def find_first_valid_path(possible_paths):
    valid_path = None

    i = 0
    while valid_path is None and i < len(possible_paths):
        if possible_paths[i].exists():
            valid_path = possible_paths[i]
        i += 1

    return valid_path


def get_structure_path(blueprint_folder: Path):
    return find_first_valid_path(
        (
            blueprint_folder / "structure.yml.jinja",
            blueprint_folder / "structure.yaml.jinja",
            blueprint_folder / "structure.yml",
            blueprint_folder / "structure.yaml",
        )
    )


def get_manifest_path(blueprint_folder: Path):
    return find_first_valid_path((blueprint_folder / "manifest.yml", blueprint_folder / "manifest.yaml"))
