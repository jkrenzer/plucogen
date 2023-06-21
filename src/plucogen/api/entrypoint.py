from dataclasses import dataclass
from importlib import metadata
from typing import Union, Tuple, List

from plucogen.logging import getLogger

log = getLogger(__name__)


@dataclass
class Entrypoints:
    prefix: Tuple[str] = tuple()

    @classmethod
    def get(cls, group_path: Tuple[str] = tuple()) -> List:
        group = ".".join(cls.prefix + group_path)
        log.debug("Looking up entrypoints for %s", group)
        return metadata.entry_points().select(group=group)

    @classmethod
    def create_entrypoints(
        cls, group_prefix_path: Union[Tuple[str], str] = None
    ) -> "Entrypoints":
        if isinstance(group_prefix_path, (str, None)):
            if group_prefix_path is None:
                group_prefix_path = __name__
            group_prefix_path = tuple(group_prefix_path.split("."))
            if len(group_prefix_path) == 1:
                group_prefix_path = cls.prefix + group_prefix_path[1:]
        log.debug("Creating entrypoints for %s", ".".join(group_prefix_path))
        return type(
            "Entrypoints",
            (cls,),
            {"prefix": group_prefix_path},
        )
