from itertools import zip_longest
from typing import List, Union

from plucogen.logging import getLogger

log = getLogger(__name__)

str


class ModulePath(object):
    separator: str = "."

    @classmethod
    def _enforce_absolute(cls, path: List[str]) -> List[str]:
        return list(filter(None, path))

    @classmethod
    def _enforce_relative(cls, path: List[str], level=1) -> List[str]:
        return ["" for n in range(level)] + cls._enforce_absolute(path)

    @classmethod
    def _rectify(cls, path: List[str]) -> List[str]:
        path = list(path)
        return path[:1] + cls._enforce_absolute(path[1:])

    @classmethod
    def split_str(cls, string: str) -> List[str]:
        raw_result: List[str] = string.split(cls.separator)
        return cls._rectify(raw_result)

    def relative(self) -> bool:
        return self._path[:1] == [""]

    def absolute(self) -> bool:
        return not self.relative()

    def __str__(self) -> str:
        return self.separator.join(self._path)

    @property
    def as_str(self) -> str:
        return self.__str__()

    def upperCamelCase(self) -> str:
        return "".join([p.capitalize() for p in self._enforce_absolute(self._path)])

    def __init__(self, *args: Union[str, "ModulePath"]) -> None:
        self._path: List[str] = list()
        log.debug("Building ModulePath from %s", args)
        if all(map(lambda a: isinstance(a, str), args)):
            if len(args) > 1:
                self._path = self._rectify(args)
            elif len(args) == 1:
                if len(args[0]) > 0:
                    self._path = self.split_str(args[0])
        elif len(args) == 1 and isinstance(args[0], self.__class__):
            self._path = self._rectify(args[0]._path)
        log.debug("Analysis yielded structure %s", self._path)

    def __getitem__(self, at: Union[int, slice]) -> Union["ModulePath", None]:
        if isinstance(at, int) and -len(self._path) <= at < len(self._path):
            return ModulePath(*[self._path.__getitem__(at)])
        elif isinstance(at, slice):
            return ModulePath(*self._path.__getitem__(at))
        else:
            return None

    def local_name(self) -> Union["ModulePath", None]:
        return self[-1]

    def __add__(self, other: Union["ModulePath", str]) -> "ModulePath":
        if isinstance(other, str):
            other_path: List[str] = self.split_str(other)
        else:
            other_path = self._enforce_absolute(other._path)
        return ModulePath(*(self._path + other_path))

    def __sub__(self, other: Union["ModulePath", str]) -> "ModulePath":
        if isinstance(other, str):
            other_path: List[str] = self.split_str(other)
        else:
            other_path = self._rectify(other._path)
        result = []
        for p, q in zip_longest(self._path, other_path):
            if p == q:
                continue
            elif q == None:
                result.append(p)
            elif p == None:
                result.append(q)
            else:
                raise ValueError(f"{other} is no ancestor of {self}!")
        result = ModulePath(*result)
        log.debug("Created path %s from %s - %s", result, self, other)
        return result

    def subtract(
        self, other: "ModulePath", strict: bool = True
    ) -> Union["ModulePath", None]:
        if strict:
            return self.__sub__(other)
        else:
            try:
                return self.__sub__(other)
            except ValueError as e:
                return None

    def ancestor_of(self, other: "ModulePath") -> bool:
        return False if self.subtract(other, strict=False) is None else True

    def parent(self) -> "ModulePath":
        return ModulePath(*self._path[:-1])

    def get_common_prefix(self, other: "ModulePath") -> "ModulePath":
        return ModulePath(*(p for p, q in zip(self._path, other._path) if p == q))

    def relative_to(self, other: "ModulePath") -> Union["ModulePath", None]:
        if self.absolute():
            return self.subtract(other, strict=False)
        else:
            return self
