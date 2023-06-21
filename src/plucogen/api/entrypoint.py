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
        if group_prefix_path is None:
            group_prefix_path = cls.prefix + (__name__,)
        elif isinstance(group_prefix_path, str):
            group_prefix_path = cls.prefix + (group_prefix_path,)
        log.debug("Creating entrypoints for %s", ".".join(group_prefix_path))
        return cls(prefix=group_prefix_path)
