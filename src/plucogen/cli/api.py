from ast import In
from socket import inet_ntoa
from plucogen.api.v0.cli import Interface as _Interface


class Interface(_Interface):
    name = "core"
    pass


Interface.register()
