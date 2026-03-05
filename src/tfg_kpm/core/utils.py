import sys
from rich.console import Console
import requests
from tomlkit import parse

console = Console()


def fetch_toml(package: str, branch: str) -> dict:
    """
    Returns the parsed contents of a registry file from GitHub.

    Parmaters
    ---------
    package: str
        The package you want to return from.
    branch: str
        The package's branch.
    """
    author, repository = package.split("/")
    name = package_name(package, branch)

    url = (
        f"https://raw.githubusercontent.com/{author}/{repository}/{branch}/registry.toml"
    )

    response = requests.get(url)

    if not response.ok:
        error(f"Failed to fetch [red]registry.toml[/red] from [red]{name}[/red]")

    data = parse(response.text)

    if "package" not in data["tfg-kpm"]:
        error(
            'Failed to find [red]"package"[/red] section in '
            f"[red]registry.toml[/red] from [red]{name}[/red]"
        )

    return data

def package_name(package: str, branch: str) -> str:
    """
    Returns a formatted version of a package name.

    Parameters
    ----------
    package: str
        The package you want to format.
    branch: str
        The branch of the package used for formatting.
    """
    return f"{package}@{branch}"

def error(message: str) -> None:
    """
    Outputs a formatted error and stops execution.

    Parameters
    ----------
    message: str
        The message you want to output
    """

    console.print(f"[bold red]ERROR[/bold red] — [white]{message}[/white]")
    sys.exit(1)
    
    
def insert_after(lst, search_value, value):
    try:
        lst.insert(lst.index(search_value)+1, value)
    except ValueError:
        lst.append(search_value)
        
def format_strings(strings):
    formatted_list = []
    
    for s in strings:
        if any(c.isspace() for c in s):
            error("[red]Class names[/red] cannot contain [red]whitespace[/red]")
        
        s = "   " + s
        
        if not s.endswith("(event)"):
            s = s + "(event)"
        
        formatted_list.append(s)
    
    return formatted_list