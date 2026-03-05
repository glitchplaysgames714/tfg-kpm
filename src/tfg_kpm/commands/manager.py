from ..core.package import Package
from ..core.utils import error
from pathlib import Path
import requests
import io
import zipfile
import shutil

from tfg_kpm.core.utils import package_name

def install_package(repository: str, branch: str):
    if repository.count("/") != 1:
            error("Invalid package format, expected [red]author/repo[/red]")
    data = Package.from_git(repository, branch)
    author, repository = repository.split("/")
    zip_url = f"https://github.com/{author}/{repository}/archive/refs/heads/{branch}.zip"
    destination = Path.cwd() / "kubejs" / "server_scripts" / "external_packages" / data.name
    
    name = package_name(repository, branch)
    
    if destination.is_dir():
        error(f"Package [red]{name}[/red] is already installed")
    
    destination.mkdir(parents=True, exist_ok=False)
    
    response = requests.get(zip_url)
    
    if not response.ok:
        error(f"Failed to fetch [red]{name}[/red]")
    
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
    server_lines = main_server_script.read_text(encoding="utf-8").splitlines()
    new_server_lines = []
    
    recipe_marker = "ServerEvents.recipes(event => {"
    itemtag_marker = "ServerEvents.tags('item', event => {"
    blocktag_marker = "ServerEvents.tags('block', event => {"
    fluidtag_marker = "ServerEvents.tags('fluid', event => {"
    
    
    for line in server_lines:
        new_server_lines.append(line)

        # Determine which marker matches this line
        if recipe_marker in line:
            for s in data.recipes:
                new_server_lines.append(s + "\n")
        elif itemtag_marker in line:
            for s in data.itemtags:
                new_server_lines.append(s + "\n")
        elif blocktag_marker in line:
            for s in data.blocktags:
                new_server_lines.append(s + "\n")
        elif fluidtag_marker in line:
            for s in data.fluidtags:
                new_server_lines.append(s + "\n")

    # Write everything back safely
    with main_server_script.open("w", encoding="utf-8") as f:
        f.writelines(new_server_lines)
