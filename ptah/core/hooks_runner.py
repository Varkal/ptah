import importlib.util
from pathlib import Path
from .exceptions import InvalidBlueprint

identity = lambda x: x


class HooksRunner:
    hooks = None

    def setup(self, path: Path):
        try:
            if path.exists():
                spec = importlib.util.spec_from_file_location("hooks", path)
                hooks_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(hooks_module)
                self.hooks = getattr(hooks_module, "Hooks")()
        except Exception:
            raise InvalidBlueprint("hooks file should contain an Hooks class")

    def run(self, step: str, ctx: dict) -> dict:
        if self.hooks:
            return getattr(self.hooks, step, identity)(ctx)

        return ctx

