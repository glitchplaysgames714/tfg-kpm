from dataclasses import dataclass, field
from pathlib import Path

from .utils import error


@dataclass
class Errors:

    errors: list[str] = field(default_factory=list[str])

    @staticmethod
    def invalid_server() -> None:
        if Path("kubejs/server_scripts/main_server_script.js").is_file():
            return

        error("""Attempted to use [red]tfg-kpm[/red] command on an [red]invalid server[/red]
              are you sure your in the correct directory?""")

    def check(self):
        for project_error in self.errors:
            getattr(self, project_error)()

