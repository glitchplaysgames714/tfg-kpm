from .utils import error, fetch_toml, format_strings
from dataclasses import dataclass
from typing import Self
from rich.progress import Progress, SpinnerColumn, TextColumn

@dataclass
class Package:
    name: str
    recipes: list[str]
    itemtags: list[str]
    blocktags: list[str]
    fluidtags: list[str]
    
    
    @classmethod
    def from_git(cls, package:str, branch:str) -> Self:
        with Progress(
            SpinnerColumn(finished_text="✅"),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(description=f"Fetching package data from {package}@{branch}")
            if package.count("/") != 1:
                error("Invalid package format, expected [red]author/repo[/red]")
            
            data = fetch_toml(package, branch)
            
            if not data or "tfg-kpm" not in data or "main" not in data["tfg-kpm"] or "package" not in data["tfg-kpm"]:
                error("Invalid [red]registry.toml[/red]")
            
            main_data = data["tfg-kpm"]["main"]
            package_data = data["tfg-kpm"]["package"]
            if "name" not in main_data:
                error("Missing [red]name[/red] field in [red]registry.toml[/red]")
            if "recipes" not in package_data and "itemtags" not in package_data and "blocktags" not in package_data and "fluidtags" not in package_data:
                error("Empty [red]package[/red] field in [red]registry.toml[/red] this package does nothing!")
            
            fields = {
                "name": main_data["name"],
                "recipes": format_strings(package_data.get("recipes", [])),
                "itemtags": format_strings(package_data.get("itemtags", [])),
                "blocktags": format_strings(package_data.get("blocktags", [])),
                "fluidtags": format_strings(package_data.get("fluidtags", []))
            }
            
        return cls(**fields)
        
        
        