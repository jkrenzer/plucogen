from typing import cast
from typer import Typer

from plucogen.logging import getLogger
from plucogen.api.v0.cli import Interface as _Interface

log = getLogger(__name__)

app = Typer()

class Interface(_Interface):
    name = "core"
    app = app

Interface.register()

apis = Interface.get_registry().get_apis()

for cname, api in apis.items():
    api = cast(_Interface, api)
    if api.name not in ("core", "cli"):
        log.debug(f"Registering CLI app {api.name} for API {cname}")
        Interface.app.add_typer(api.app, name=api.name)
log.info("Registered all CLI apps")