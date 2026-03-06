import typer
from .core.errors import Errors
from .commands.manager import install_package, list_packages, uninstall_package

app = typer.Typer()

@app.command()
def install(repository: str, branch: str = "main"):
    Errors(["invalid_server"]).check()
    
    install_package(repository, branch)

@app.command()
def list():
    Errors(["invalid_server"]).check()
    
    
    for package in list_packages():
        print(package)

@app.command()
def uninstall(package: str):
    Errors(["invalid_server"]).check()
    
    uninstall_package(package)
    
    

@app.command()
def hello(name: str):
    print(f"Hello {name}")


@app.command()
def goodbye(name: str, formal: bool = False):
    if formal:
        print(f"Goodbye Ms. {name}. Have a good day.")
    else:
        print(f"Bye {name}!")

app()