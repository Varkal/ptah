from bullet import Bullet, YesNo
from pathlib import Path


class BlueprintManager:
    def __init__(self):
        self.config = None

    def setup(self, config: dict):
        self.config = config

    def get_blueprint_folder(self, blueprint_name: str = None):
        library_folder = Path(self.config.get("library_folder", "~/.ptah/library/")).expanduser()

        if blueprint_name:
            return library_folder / blueprint_name

        available_shelvings = library_folder.iterdir()
        available_blueprints = {}

        for shelving in available_shelvings:
            for path in shelving.iterdir():
                available_blueprints[f" {shelving.name}/{path.name}"] = path

        ui = Bullet(prompt="Choose your blueprint:", choices=list(available_blueprints.keys()))

        return available_blueprints[ui.launch()]
