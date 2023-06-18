from pathlib import Path
from typing import Union, List

from logging import getLogger

log = getLogger(__name__)


class FileConfig:
    default_search_paths: List[Union[Path, str]] = ["/", "./"]

    def __init__(self, search_paths: Union[List[Union[Path, str]], None] = None):
        if search_paths is None:
            search_paths = self.default_search_paths
        self.set_search_paths(search_paths)

    def set_search_paths(self, searchpaths: List[Union[Path, str]]):
        search_paths = [p if isinstance(p, Path) else Path(p) for p in searchpaths]
        self._search_paths = list(dict.fromkeys(search_paths))

    def add_search_paths(self, searchpaths: List[Union[Path, str]]):
        self.set_search_paths(self._search_paths + searchpaths)

    def get_search_paths(self):
        return self._search_paths


config = FileConfig()


set_search_paths = config.set_search_paths
get_search_paths = config.get_search_paths


def find_file(path: Union[Path, str]) -> Union[Path, None]:
    log.debug("Searching file %s", str(path))
    if isinstance(path, str):
        path = Path(path)
    # First check the given path
    if path.is_file():
        log.debug("Found file %s", str(path))
        return path
    for search_path in get_search_paths():
        candidate = search_path / path
        log.debug("Evaluating path %s", str(candidate))
        if candidate.is_file():
            log.debug("Found file %s at path %s", str(path), str(candidate))
            return candidate
    log.info("File %s could not be found", str(path))
    return None
