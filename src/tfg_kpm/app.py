import typer
from .core.errors import Errors
from .commands.manager import install_package

app = typer.Typer()

@app.command()
def install(package: str, branch: str = "main"):
    Errors(["invalid_server"]).check()
    
    install_package(package, branch)


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