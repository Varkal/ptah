from chuda import App, autorun
from os import getenv

from .commands.create import CreateCommand

@autorun()
class PtahApp(App):
    
    config_path = [
        f"{getenv('HOME')}/.ptahrc"
    ]
    config_parser = "yaml"

    subcommands = [
        CreateCommand
    ]
