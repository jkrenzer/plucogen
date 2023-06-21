import jsonschema

from plucogen.api.v0.handler import Interface

InputData = Interface.InputData
Outputdata = Interface.OutputData


def validate(input: InputData) -> Outputdata:
    pass
