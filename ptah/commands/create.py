from chuda import Command, Parameter, Option
from pathlib import Path
from bullet import Bullet, YesNo
from shutil import rmtree, copy
from ..core.exceptions import InvalidBlueprint
from jinja2 import Environment, FileSystemLoader

import sys
import yaml


class CreateCommand(Command):
    command_name = "create"

    arguments = [Parameter("name"), Option(["--blueprint", "-b"], default=None)]

    ctx = {}

    def main(self):
        blueprint_folder = self.get_blueprint_folder()

        if not blueprint_folder.exists():
            raise InvalidBlueprint(f"{blueprint_folder} doesn't exist")

        self.ctx["blueprint_folder"] = blueprint_folder

        target_folder = Path(".") / self.arguments.name

        self.ctx["folder_name"] = self.arguments.name
        self.ctx["target_folder"] = target_folder

        if target_folder.exists():
            should_continue = YesNo(
                prompt=f"{target_folder} already exist. Do you want to delete it ? "
            ).launch()

            if not should_continue:
                sys.exit(0)

            rmtree(target_folder)

        target_folder.mkdir()

        structure_file_paths = (
            blueprint_folder / "structure.yml.jinja",
            blueprint_folder / "structure.yaml.jinja",
            blueprint_folder / "structure.yml",
            blueprint_folder / "structure.yaml",
        )

        structure_file_path = None

        i = 0
        while structure_file_path is None and i < len(structure_file_paths):
            if structure_file_paths[i].exists():
                structure_file_path = structure_file_paths[i]
            i += 1

        if structure_file_path is None:
            raise InvalidBlueprint(f"{blueprint_folder}/structure.yml doesn't exist")

        structure = yaml.safe_load(structure_file_path.read_text())

        self.create_structure(structure, target_folder, blueprint_folder)

    def get_blueprint_folder(self):
        if self.arguments.blueprint:
            return (
                Path(self.config["library_folder"]) / self.arguments.blueprint
            ).expanduser()

        library_folder = Path(self.config["library_folder"]).expanduser()
        available_blueprints = {
            f" {path.name}": path for path in library_folder.iterdir()
        }
        ui = Bullet(
            prompt="Choose your blueprint:", choices=list(available_blueprints.keys())
        )

        return available_blueprints[ui.launch()]

    def create_jinja_env(self, blueprint_folder: Path):
        env = Environment(loader=FileSystemLoader(str(blueprint_folder)))
        env.globals = self.ctx
        return env

    def is_empty_directory_marker(self, value):
        return isinstance(value, list) or isinstance(value, tuple) or value is None

    def create_structure(self, dict_: dict, base_path: Path, blueprint_folder: Path):
        for key, value in dict_.items():
            new_path = base_path / key

            if isinstance(value, dict):  # Directory
                new_path.mkdir()
                self.create_structure(value, new_path, blueprint_folder)
            elif (self.is_empty_directory_marker(value)):  # Directory
                new_path.mkdir()
            elif isinstance(value, str):  # File
                source_path = blueprint_folder / "src" /value
                if value.endswith(".jinja"):  # Template
                    new_path.touch()
                    env = self.create_jinja_env(blueprint_folder)
                    template = env.get_template(f"src/{value}")
                    new_path.write_text(template.render())
                else:
                    copy(source_path, new_path)
            else:
                raise InvalidBlueprint(f"structure.yml file as invalid value: {value}")
