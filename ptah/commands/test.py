from chuda import Command
from ..core.context_builder import ContextBuilder
from pathlib import Path
import yaml

class TestCommand(Command):
    command_name = "test"
    def main(self):
        manifest = yaml.safe_load(Path("./library/chuda-app/manifest.yml").read_text())
        utils_path = str(Path("./library/chuda-app/utils.py").resolve())
        self.logger.info(ContextBuilder().build_context(manifest, utils_path))
