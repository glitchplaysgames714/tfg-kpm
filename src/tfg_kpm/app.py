import time
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from .commands.manager import install_package, list_packages, uninstall_package, update_packages
from .core.errors import Errors
from .core.utils import error

app = typer.Typer()

@app.command()
def install(repository: str, branch: str = "main"):
    Errors(["invalid_server"]).check()

    console = Console()
    start = time.perf_counter()

    package = install_package(repository, branch)

    end = time.perf_counter()
    elapsed = end - start

    if elapsed < 1:
        console.log(f"""Installed {package} in [bright_cyan]{elapsed * 1000:.0f}[/bright_cyan]
                    milliseconds""", style="bold green")
    elif elapsed < 60:
        console.log(f"Installed {package} in [bright_cyan]{elapsed:.2f}[/bright_cyan] seconds", style="bold green")
    else:
        minutes = elapsed / 60
        console.log(f"Installed {package} in [bright_cyan]{minutes:.2f}[/bright_cyan] minutes", style="bold green")

@app.command()
def list():
    Errors(["invalid_server"]).check()

    packages = list_packages()

    console = Console()
    table = Table(title="Installed packages")
    table.add_column("Name")
    table.add_column("Repo")
    table.add_column("Branch")

    for package in packages:
        gitrepofile = Path.cwd() / "kubejs" / "server_scripts" / "external_packages" / package / "gitrepo"
        if gitrepofile.is_file():
            repo = gitrepofile.read_text(encoding="utf-8")
            repo, branch = repo.split("@")
            table.add_row(package, repo, branch)
        else:
            table.add_row(package, "Unknown", "Unknown")

    console.print(table)

@app.command()
def uninstall(package: str):
    Errors(["invalid_server"]).check()


    installedpackages = list_packages()
    if package not in installedpackages:
        error(f"{package} is [red]not[/red] installed!")
    console = Console()
    packagedir = Path.cwd() / "kubejs" / "server_scripts" / "external_packages" / package

    console.log(f"Found existing installation: {package}", style="bold green")
    console.log(f"Uninstalling {package}:")
    console.log("  Would remove:")
    console.log(f"    [bright_cyan]{packagedir.as_posix()}[/bright_cyan]")
    typer.confirm("Proceed?", abort=True)
    start = time.perf_counter()

    uninstall_package(package, packagedir)

    end = time.perf_counter()
    elapsed = end - start

    if elapsed < 1:
        console.log(f"""Uninstalled {package} in [bright_cyan]{elapsed * 1000:.0f}[/bright_cyan]
                    milliseconds""", style="bold green")
    elif elapsed < 60:
        console.log(f"Uninstalled {package} in [bright_cyan]{elapsed:.2f}[/bright_cyan] seconds", style="bold green")
    else:
        minutes = elapsed / 60
        console.log(f"Uninstalled {package} in [bright_cyan]{minutes:.2f}[/bright_cyan] minutes", style="bold green")

@app.command()
def update():

    Errors(["invalid_server"]).check

    console = Console()
    start = time.perf_counter()

    typer.confirm("Update all packages?", abort=True)

    update_packages()

    end = time.perf_counter()
    elapsed = end - start

    if elapsed < 1:
        console.log(f"""Updated all packages in [bright_cyan]{elapsed * 1000:.0f}[/bright_cyan]
                    milliseconds""", style="bold green")
    elif elapsed < 60:
        console.log(f"Updated all packages in [bright_cyan]{elapsed:.2f}[/bright_cyan] seconds", style="bold green")
    else:
        minutes = elapsed / 60
        console.log(f"Updated all packages in [bright_cyan]{minutes:.2f}[/bright_cyan] minutes", style="bold green")

