from ..core.package import Package
from ..core.utils import error, insert_after, package_name
from pathlib import Path
import requests
import sys
import io
import zipfile
import shutil
import rich
from rich.progress import Progress, SpinnerColumn, TextColumn


def install_package(repository: str, branch: str):
    if repository.count("/") != 1:
            error("Invalid package format, expected [red]author/repo[/red]")
    data = Package.from_git(repository, branch)
    with Progress(
        SpinnerColumn(finished_text="✅"),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task(description="Fetching package from github")
        author, repository = repository.split("/")
        zip_url = f"https://github.com/{author}/{repository}/archive/refs/heads/{branch}.zip"
        destination = Path.cwd() / "kubejs" / "server_scripts" / "external_packages" / data.name
    
        name = package_name(repository, branch)
    
        if destination.is_dir():
            progress.remove_task(task)
            error(f"Package [red]{data.name}[/red] is already installed")
    
        destination.mkdir(parents=True, exist_ok=False)
    
        response = requests.get(zip_url)
    
        if not response.ok:
            progress.remove_task(task)
            error(f"Failed to fetch [red]{name}[/red]")
        progress.remove_task(task)
        progress.add_task(description=f"Extracting package files from {name}")
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
    
    main_server_script = Path.cwd() / "kubejs" / "server_scripts" / "main_server_script.js"
    server_lines = []
    
    with rich.progress.open(main_server_script, "r", encoding="utf-8", description="reading main_server_script.js") as f:
        server_lines = f.read().splitlines()
    
    recipe_marker = "ServerEvents.recipes(event => {"
    itemtag_marker = "ServerEvents.tags('item', event => {"
    blocktag_marker = "ServerEvents.tags('block', event => {"
    fluidtag_marker = "ServerEvents.tags('fluid', event => {"
    with Progress(
        SpinnerColumn(finished_text="✅"),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
         recipetask = progress.add_task(description="Defining recipes in main_server_script.js")
    for v in data.recipes:
        insert_after(server_lines, recipe_marker, v)
        progress.remove_task(recipetask)
        itemtask = progress.add_task(description="Defining item tags in main_server_script.js")
    for v in data.itemtags:
        insert_after(server_lines, itemtag_marker, v)
        progress.remove_task(itemtask)
        blocktask = progress.add_task(description="Defining block tags in main_server_script.js")
    for v in data.blocktags:
        insert_after(server_lines, blocktag_marker, v)
        progress.remove_task(blocktask)
        fluidtask = progress.add_task(description="Defining fluid tags in main_server_script.js")
    for v in data.fluidtags:
        insert_after(server_lines, fluidtag_marker, v)
        progress.remove_task(fluidtask)
    print("Finished defining classes")
    
    with rich.progress.open(main_server_script, "w", encoding="utf-8", description="writing to main_server_script.js") as f:
        for item in server_lines:
            f.write(f"{item}\n")
        
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
    
    
    
