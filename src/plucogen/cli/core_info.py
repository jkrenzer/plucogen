from typer import Typer

from plucogen.api.v0 import Registry, cli

app = Typer(help="Dump core informations")


class Interface(cli.Interface):
    name = "core-info"
    app = app


Interface.register()


@app.callback(invoke_without_command=True)
def main() -> None:
    print("Core Registry:")
    apis = Registry.get_all_apis()
    for name, interface in apis.items():
        print(f"{name}: {repr(interface)}, {interface.module}")
