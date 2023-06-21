from pathlib import Path
from typing import List

from plucogen.api.v0.consumer import Interface as ApiI, Registry


class Interface(ApiI):
    name = "file"
    module = __name__

    @classmethod
    def read_files(cls, filepaths: List[Path]):
        return [f.read_text() for f in filepaths]

    @classmethod
    def consume(cls, inputData: ApiI.InputData) -> ApiI.OutputData:
        filepaths = [f for f in inputData.resources if isinstance(f, Path)]
        return ApiI.OutputData(
            options=inputData.options,
            data=cls.read_files(filepaths),
            return_code=inputData.return_code,
            messages=inputData.messages,
        )


Interface.register()
