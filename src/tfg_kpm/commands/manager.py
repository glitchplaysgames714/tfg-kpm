from ..core.package import Package
from ..core.utils import error, insert_after, package_name
from pathlib import Path
import requests
import sys
import io
import zipfile
import shutil
from rich.console import Console


def install_package(repository: str, branch: str):
    
    console = Console()
    spinner = console.status("Getting package metadata from github")
    if repository.count("/") != 1:
            console.log("Failed to get package metadata", style="bold red")
            error("Invalid package format, expected [red]author/repo[/red]")
    data = Package.from_git(repository, branch)
    author, repository = repository.split("/")
    zip_url = f"https://github.com/{author}/{repository}/archive/refs/heads/{branch}.zip"
    destination = Path.cwd() / "kubejs" / "server_scripts" / "external_packages" / data.name
    
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
        base_folder = f"{repository}-{branch}/"
        for member in z.namelist():
            if member.startswith(base_folder + "server_scripts/") or member == base_folder + "registry.toml":
                relative_path = member[len(base_folder):]
                if relative_path.startswith("server_scripts/"):
                    relative_path = relative_path[len("server_scripts/"):]

                    target_path = Path(destination) / relative_path

                    if member.endswith("/"):
                        # Skip directories, mkdir handles them below
                        continue

                    target_path.parent.mkdir(parents=True, exist_ok=True)

                    with z.open(member) as src, open(target_path, "wb") as dst:
                        shutil.copyfileobj(src, dst)
    console.log("Finished extracting package to server scripts", style="bold green")
    spinner.update("Reading main_server_script.js")
    
    main_server_script = Path.cwd() / "kubejs" / "server_scripts" / "main_server_script.js"
    server_lines = []
        
    with open(main_server_script, "r", encoding="utf-8") as f:
        server_lines = f.read().splitlines()
    console.log("Finished reading main_server_script.js", style="bold green")
    recipe_marker = "ServerEvents.recipes(event => {"
    itemtag_marker = "ServerEvents.tags('item', event => {"
    blocktag_marker = "ServerEvents.tags('block', event => {"
    fluidtag_marker = "ServerEvents.tags('fluid', event => {"
    
    spinner.update("Defining recipe classes")
    for v in data.recipes:
        insert_after(server_lines, recipe_marker, v)
        console.log(f"Finished Defining [bright_magenta]{v.replace(" ", "").replace("(event)", "")}[/bright_magenta]", style="bold green")
    console.log("Finished Defining recipe classes", style="bold green")
    spinner.update("Defining item tag classes")
    for v in data.itemtags:
        insert_after(server_lines, itemtag_marker, v)
        console.log(f"Finished Defining [bright_magenta]{v.replace(" ", "").replace("(event)", "")}[/bright_magenta]", style="bold green")
    console.log("Finished Defining item tag classes", style="bold green")
    spinner.update("Defining block tag classes")
    for v in data.blocktags:
        insert_after(server_lines, blocktag_marker, v)
        console.log(f"Finished Defining [bright_magenta]{v.replace(" ", "").replace("(event)", "")}[/bright_magenta]", style="bold green")
    console.log("Finished Defining block tag classes", style="bold green")
    spinner.update("Defining fluid tag classes")
    for v in data.fluidtags:
        insert_after(server_lines, fluidtag_marker, v)
        console.log(f"Finished Defining [bright_magenta]{v.replace(" ", "").replace("(event)", "")}[/bright_magenta]", style="bold green")
    console.log("Finished Defining fluid tag classes", style="bold green")
    spinner.update("Writing to main_server_script.js")
    with open(main_server_script, "w", encoding="utf-8") as f:
        for item in server_lines:
            f.write(f"{item}\n")
    console.log("Finished writing to main_server_script.js", style="bold green")
    console.log(f"Successfully installed {data.name}", style="bold green")
        
def list_packages():
    packagefolder = Path.cwd() / "kubejs" / "server_scripts" / "external_packages"
    if not packagefolder.is_dir():
        print("No packages installed")
        sys.exit(0)
    packages = packagefolder.iterdir()
    if packages is None:
        print("No packages installed")
        sys.exit(0)
    return packages
    
    
    
