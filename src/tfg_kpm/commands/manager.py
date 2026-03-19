import io
import os
import shutil
import zipfile
from pathlib import Path

import requests
import typer
from rich.console import Console
from tomlkit import load

from ..core.package import Package
from ..core.utils import error, format_strings, insert_after, package_name


def install_package(repository: str, branch: str):

    console = Console()
    with console.status("Getting package metadata from github") as spinner:
        if repository.count("/") != 1:
            console.log("Failed to get package metadata", style="bold red")
            error("Invalid package format, expected [red]author/repo[/red]")
        data = Package.from_git(repository, branch)
        author, repository = repository.split("/")
        zip_url = (
            f"https://github.com/{author}/{repository}/archive/refs/heads/{branch}.zip"
        )
        destination = (
            Path.cwd() / "kubejs" / "server_scripts" / "external_packages" / data.name
        )

        name = package_name(repository, branch)
        console.log("Finished getting package metadata", style="bold green")
        if destination.is_dir():
            error(f"Package [red]{data.name}[/red] is already installed")
        spinner.update(status="Fetching package archive")
        destination.mkdir(parents=True, exist_ok=False)

        response = requests.get(zip_url)

        if not response.ok:
            console.log("Failed to fetch package archive", style="bold red")
            error(f"Failed to fetch [red]{name}[/red]")
        console.log("Finished fetching package archive", style="bold green")
        spinner.update(status="Extracting package archive")
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            for member in z.namelist():
                path = Path(member)

                # copy server_scripts contents
                if "server_scripts" in path.parts:
                    idx = path.parts.index("server_scripts")
                    relative = Path(*path.parts[idx + 1 :])
                    target = destination / relative

                # copy registry.toml
                elif path.name == "registry.toml":
                    target = destination / "registry.toml"

                else:
                    continue

                if member.endswith("/"):
                    continue

                target.parent.mkdir(parents=True, exist_ok=True)
                with z.open(member) as src, target.open("wb") as dst:
                    dst.write(src.read())

        gitrepofile = destination / "gitrepo"
        with gitrepofile.open("w", encoding="utf-8") as f:
            f.write(author + "/" + repository + "@" + branch)

        console.log("Finished extracting package to server scripts", style="bold green")
        spinner.update("Reading main_server_script.js")

        main_server_script = (
            Path.cwd() / "kubejs" / "server_scripts" / "main_server_script.js"
        )
        server_lines = []

        server_lines = main_server_script.read_text(encoding="utf-8").splitlines()
        console.log("Finished reading main_server_script.js", style="bold green")
        recipe_marker = "ServerEvents.recipes(event => {"
        itemtag_marker = "ServerEvents.tags('item', event => {"
        blocktag_marker = "ServerEvents.tags('block', event => {"
        fluidtag_marker = "ServerEvents.tags('fluid', event => {"

        spinner.update("Defining recipe classes")
        for v in data.recipes:
            insert_after(server_lines, recipe_marker, v)
            console.log(
                f"Finished Defining [bright_magenta]{v.replace(' ', '').replace('(event)', '')}[/bright_magenta]",
                style="bold green",
            )
        console.log("Finished Defining recipe classes", style="bold green")
        spinner.update("Defining item tag classes")
        for v in data.itemtags:
            insert_after(server_lines, itemtag_marker, v)
            console.log(
                f"Finished Defining [bright_magenta]{v.replace(' ', '').replace('(event)', '')}[/bright_magenta]",
                style="bold green",
            )
        console.log("Finished Defining item tag classes", style="bold green")
        spinner.update("Defining block tag classes")
        for v in data.blocktags:
            insert_after(server_lines, blocktag_marker, v)
            console.log(
                f"inished Defining [bright_magenta]{v.replace(' ', '').replace('(event)', '')}[/bright_magenta]",
                style="bold green",
            )
        console.log("Finished Defining block tag classes", style="bold green")
        spinner.update("Defining fluid tag classes")
        for v in data.fluidtags:
            insert_after(server_lines, fluidtag_marker, v)
            console.log(
                f"Finished Defining [bright_magenta]{v.replace(' ', '').replace('(event)', '')}[/bright_magenta]",
                style="bold green",
            )
        console.log("Finished Defining fluid tag classes", style="bold green")
        spinner.update("Writing to main_server_script.js")
        with open(main_server_script, "w", encoding="utf-8") as f:
            for item in server_lines:
                f.write(f"{item}\n")
    console.log("Finished writing to main_server_script.js", style="bold green")

    return data.name


def list_packages():
    packagefolder = Path.cwd() / "kubejs" / "server_scripts" / "external_packages"
    if not packagefolder.is_dir():
        error("No packages installed")
    packages = os.listdir(packagefolder)
    if not packages:
        error("No packages installed")
    return packages


def uninstall_package(package: str, packagedir: Path):
    console = Console()
    with console.status("Parsing registry file") as spinner:
        registry = packagedir / "registry.toml"
        with open(registry, "r", encoding="utf-8") as f:
            data = load(f)
        package_data = data["tfg-kpm"]["package"]
        classes = (
            package_data.get("recipes")
            + package_data.get("itemtags")
            + package_data.get("blocktags")
            + package_data.get("fluidtags")
        )
        classes = format_strings(classes)
        console.log("Finished parsing registry file", style="bold green")
        spinner.update(status="Reading main_server_script.js")
        main_server_script = (
            Path.cwd() / "kubejs" / "server_scripts" / "main_server_script.js"
        )

        server_lines = main_server_script.read_text(encoding="utf-8").splitlines()

        console.log("Finished reading main_server_script.js", style="bold green")
        spinner.update(status="Removing class definitions")

        comparisonset = set(classes)
        server_lines = [item for item in server_lines if item not in comparisonset]

        console.log("Finished removing class definitions", style="bold green")
        spinner.update(status="Writing to main_server_script.js")

        with open(main_server_script, "w", encoding="utf-8") as f:
            for item in server_lines:
                f.write(f"{item}\n")

        console.log("Finished writing to main_server_script.js", style="bold green")
        spinner.update(status="Removing package")

        shutil.rmtree(packagedir)

        console.log("Finished removing package", style="bold green")


def update_packages():
    console = Console()
    packages = []
    oldpackages = []
    for package in list_packages():
        packagedir = (
            Path.cwd() / "kubejs" / "server_scripts" / "external_packages" / package
        )
        gitrepofile = packagedir / "gitrepo"
        if not gitrepofile.is_file():
            oldpackages.append(package)
        else:
            packages.append(package)

    if oldpackages:
        packagelist = ""
        if len(oldpackages) == 1:
            packagelist = oldpackages[0]
        elif len(oldpackages) == 2:
            packagelist = f"{oldpackages[0]} and {oldpackages[1]}"
        else:
            packagelist = (
                ", ".join(map(str, oldpackages[:-1])) + ", and " + str(oldpackages[-1])
            )

        console.log(
            f"""[bold red]The following packages were installed prior to v2.0: {packagelist}.
            Please reinstall them manually.[/bold red]"""
        )
        typer.confirm("Proceed with installing the other packages?", abort=True)

    repos = []
    for package in packages:
        gitrepofile = (
            Path.cwd()
            / "kubejs"
            / "server_scripts"
            / "external_packages"
            / package
            / "gitrepo"
        )
        repos.append(gitrepofile.read_text(encoding="utf-8"))

    for package in packages:
        uninstall_package(
            package,
            (Path.cwd() / "kubejs" / "server_scripts" / "external_packages" / package),
        )
        console.log(f"Uninstalled {package}", style="bold green")

    for repo in repos:
        frepo, fbranch = repo.split("@")
        package = install_package(frepo, fbranch)
        console.log(f"Installed {package}", style="bold green")
