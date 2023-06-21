from typing import List

from plucogen.api.v0.handler import Interface as _ApiI
from .yaml import load_yaml_string
from . import _module_name


class Interface(_ApiI):
    name = "yaml"
    module = _module_name

    @classmethod
    def handle(cls, inputData: _ApiI.InputData) -> _ApiI.OutputData:
        data = inputData.data.require()
        if isinstance(inputData.data.require(), str):
            inputData.data.set(load_yaml_string(data))
            return _ApiI.OutputData(inputData)


Interface.register()
