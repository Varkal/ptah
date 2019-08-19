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

    arguments = [
        Parameter("name"),
        Option(["--blueprint", "-b"], default=None)
    ]

    def main(self):
        if self.arguments.blueprint:
            blueprint_folder = (Path(self.config["library_folder"]) / self.arguments.blueprint).expanduser()
        else:
            library_folder = Path(self.config["library_folder"]).expanduser()
            available_blueprints = {
                f" {path.name}":path for path in 
                library_folder.iterdir()
            }
            ui = Bullet(
                prompt = "Choose your blueprint:",
                choices = list(available_blueprints.keys())
            )
            blueprint_folder = available_blueprints[ui.launch()]

        if not blueprint_folder.exists():
            raise InvalidBlueprint(f"{blueprint_folder} doesn't exist")

        target_folder = Path(".") / self.arguments.name

        if target_folder.exists():
            should_continue = YesNo(
                prompt = f"{target_folder} already exist. Do you want to delete it ? "
            ).launch()

            if not should_continue:
                sys.exit(0)
            
            rmtree(target_folder)

        target_folder.mkdir()
        
        structure_file_paths = (
            blueprint_folder / "structure.yml",
            blueprint_folder / "structure.yaml"
        )

        structure_file_path = None
        
        i = 0 
        while structure_file_path is None and i < len(structure_file_paths):
            if structure_file_paths[i].exists():
                structure_file_path = structure_file_paths[i]
            i+=1

        if structure_file_path is None:
            raise InvalidBlueprint(f"{blueprint_folder}/structure.yml doesn't exist")
        
        structure = yaml.safe_load(structure_file_path.read_text())

        self.create_structure(structure, target_folder, blueprint_folder)

    def create_context(self, blueprint_folder: Path):
        env = Environment(
            loader=FileSystemLoader(str(blueprint_folder)),
        )
        return env 
    
    def create_structure(self, dict_: dict, base_path: Path, blueprint_folder: Path):
        for key, value in dict_.items():
            new_path = base_path / key
            
            if isinstance(value, dict): # Directory
                new_path.mkdir()
                self.create_structure(value, new_path, blueprint_folder)
            elif isinstance(value, list) or isinstance(value, tuple) or value is None: # Directory
                new_path.mkdir()
            elif isinstance(value, str): # File
                source_path = blueprint_folder / value
                if value.endswith(".jinja"): # Template
                    new_path.touch()
                    print(self.create_context(blueprint_folder))
                    # TODO Detemplate
                else:
                   copy(source_path, new_path)
            else:
                raise InvalidBlueprint(f"structure.yml file as invalid value: {value}")


