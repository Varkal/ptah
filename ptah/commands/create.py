from chuda import Command, Parameter, Option
from pathlib import Path
from bullet import Bullet, YesNo
from shutil import rmtree, copy
from ..core.exceptions import InvalidBlueprint
from ..core.context_builder import ContextBuilder
from ..core.hooks_runner import HooksRunner
from jinja2 import Environment, FileSystemLoader

import sys
import yaml


class CreateCommand(Command):
    command_name = "create"

    arguments = [Parameter("name"), Option(["--blueprint", "-b"], default=None)]

    ctx = {}
    builder = ContextBuilder()
    hooks = HooksRunner()
    jinja_env = None

    def main(self):
        blueprint_folder = self.get_blueprint_folder()

        if not blueprint_folder.exists():
            raise InvalidBlueprint(f"{blueprint_folder} doesn't exist")

        self.hooks.setup(blueprint_folder / "hooks.py")

        target_folder = Path(".") / self.arguments.name

        self.ctx["blueprint_folder"] = blueprint_folder
        self.ctx["folder_name"] = self.arguments.name
        self.ctx["target_folder"] = target_folder

        self.ctx = self.hooks.run("pre_run_hook", self.ctx)

        structure_file_path = self.find_first_valid_path(
            (
                blueprint_folder / "structure.yml.jinja",
                blueprint_folder / "structure.yaml.jinja",
                blueprint_folder / "structure.yml",
                blueprint_folder / "structure.yaml",
            )
        )

        manifest_file_path = self.find_first_valid_path(
            (blueprint_folder / "manifest.yml", blueprint_folder / "manifest.yaml")
        )

        if manifest_file_path is None:
            raise InvalidBlueprint(f"{blueprint_folder}/manifest.yml doesn't exist")

        if structure_file_path is None:
            raise InvalidBlueprint(
                f"Neither {blueprint_folder}/structure.yml nor {blueprint_folder}/structure.yml {blueprint_folder}/structure.yml.jinja exist"
            )

        self.create_target_folder()

        manifest = yaml.safe_load(manifest_file_path.read_text())

        utils_path = blueprint_folder / "utils.py"
        if utils_path.exists():
            utils_path = str(utils_path.resolve())
        else:
            utils_path = None

        self.ctx = self.hooks.run("pre_prompt_hook", self.ctx)
        self.ctx.update(self.builder.build_context(manifest, utils_path))
        self.ctx = self.hooks.run("post_prompt_hook", self.ctx)

        self.jinja_env = self.create_jinja_env()

        structure_content = structure_file_path.read_text()
        if structure_file_path.suffix == ".jinja":
            structure_content = self.jinja_env.from_string(structure_content).render()

        structure = yaml.safe_load(structure_file_path.read_text())

        self.create_structure(structure, target_folder, blueprint_folder)
        self.ctx = self.hooks.run("post_run_hook", self.ctx)

    def create_target_folder(self):
        target_folder = self.ctx["target_folder"]

        if target_folder.exists():
            should_continue = YesNo(prompt=f"{target_folder} already exist. Do you want to delete it ? ").launch()

            if not should_continue:
                sys.exit(0)

            rmtree(target_folder)

        target_folder.mkdir()

    def get_blueprint_folder(self):
        if self.arguments.blueprint:
            return (Path(self.config["library_folder"]) / self.arguments.blueprint).expanduser()

        library_folder = Path(self.config["library_folder"]).expanduser()
        available_blueprints = {f" {path.name}": path for path in library_folder.iterdir()}
        ui = Bullet(prompt="Choose your blueprint:", choices=list(available_blueprints.keys()))

        return available_blueprints[ui.launch()]

    def create_jinja_env(self):
        env = Environment(loader=FileSystemLoader(str(self.ctx["blueprint_folder"])))
        env.globals = self.ctx
        return env

    def find_first_valid_path(self, possible_paths):
        valid_path = None

        i = 0
        while valid_path is None and i < len(possible_paths):
            if possible_paths[i].exists():
                valid_path = possible_paths[i]
            i += 1

        return valid_path

    def is_empty_directory_marker(self, value):
        return isinstance(value, list) or isinstance(value, tuple) or value is None

    def create_structure(self, dict_: dict, base_path: Path, blueprint_folder: Path):
        for key, value in dict_.items():
            new_path = base_path / key

            if isinstance(value, dict):  # Directory
                new_path.mkdir()
                self.create_structure(value, new_path, blueprint_folder)
            elif self.is_empty_directory_marker(value):  # Directory
                new_path.mkdir()
            elif isinstance(value, str):  # File
                source_path = blueprint_folder / "src" / value
                if value.endswith(".jinja"):  # Template
                    new_path.touch()
                    template = self.jinja_env.get_template(f"src/{value}")
                    new_path.write_text(template.render())
                else:
                    copy(source_path, new_path)
            else:
                raise InvalidBlueprint(f"structure.yml file as invalid value: {value}")
