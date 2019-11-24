from chuda import App, autorun
from os import getenv

from .commands.create import CreateCommand
from .commands.test import TestCommand

@autorun()
class PtahApp(App):

    config_path = [f"{getenv('HOME')}/.ptahrc"]
    config_parser = "yaml"

    subcommands = [CreateCommand, TestCommand]
