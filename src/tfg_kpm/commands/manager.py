from ..core.package import Package
from ..core.utils import error
from pathlib import Path
import requests
import io
import zipfile

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
        z.extractall(path=destination,members=[m for m in z.namelist() if m.startswith(base_folder + "server_scripts/") or m == base_folder + "registry.toml"])
    
    main_server_script = Path.cwd() / "kubejs" / "server_scripts" / "main_server_script.js"
    server_lines = main_server_script.read_text(encoding="utf-8").splitlines()
    new_server_lines = []
    
    recipe_marker = "ServerEvents.recipes(event => {"
    itemtag_marker = "ServerEvents.tags('item', event => {"
    blocktag_marker = "ServerEvents.tags('block', event => {"
    fluidtag_marker = "ServerEvents.tags('fluid', event => {"
    
    
    for line in server_lines:
        new_server_lines.append(line)
        
        if recipe_marker in line:
            new_server_lines.extend(data.recipes)
        elif itemtag_marker in line:
            new_server_lines.extend(data.itemtags)
        elif blocktag_marker in line:
            new_server_lines.extend(data.blocktags)
        elif fluidtag_marker in line:
            new_server_lines.extend(data.fluidtags)
            
    main_server_script.write_text("\n".join(new_server_lines) + "\n", encoding="utf-8")

    