from dataclasses import dataclass
from typing import Tuple, Union, Iterable


class ArbitraryPath:
    parts: Tuple[str]
    delimiter: str

    def _from_string(self, string: str, delimiter: str):
        parts = (p for p in string.split(delimiter) if p != "")
        self.parts = parts
        self.delimiter = delimiter

    def _from_iterable(self, iter: Iterable[str], delimiter: str):
        self.parts = (p for p in iter if p != "")
        self.delimiter = delimiter

    def __init__(self, source, delimiter):
        if isinstance(source, str):
            self._from_string(source, delimiter)
        elif isinstance(source, Iterable):
            self._from_iterable(source, delimiter)

    def __add__(self, other: Union["ArbitraryPath", str]) -> "ArbitraryPath":
        if isinstance(other, str):
            other = ArbitraryPath(other)
        parts = self.parts + other.parts
        return ArbitraryPath(parts, self.delimiter)

    def relative_to(self, other: Union["ArbitraryPath", str]) -> "ArbitraryPath":
        if isinstance(other, str):
            other = ArbitraryPath(other)
        parts = (
            p
            for i, p in enumerate(self.parts)
            if i < len(other.parts) and p != other.parts[i]
        )
        return ArbitraryPath(parts, self.delimiter)


class DotPath(ArbitraryPath):
    def __init__(self, source, delimiter):
        super().__init__(source, delimiter)
