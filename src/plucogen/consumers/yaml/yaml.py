from pathlib import Path
from typing import Union, Dict, List, Any
from logging import getLogger

from plucogen.file import find_file

from . import get_yaml_instance

log = getLogger(__name__)


def load_yaml_string(source: Union[str, Path], context: Union[Dict, Any] = {}):
    """Load YAML from a string or file-descriptor"""

    yaml = get_yaml_instance()
    data = None
    try:
        if isinstance(source, Path):
            log.debug("Reading YAML from path %s", str(source))
        else:
            log.debug(
                "Reading YAML from value given of length %i: %s", len(source), source
            )
        data = yaml.load(source)
        log.debug(
            "Read YAML of root length %i and type %s", len(data), type(data).__name__
        )
        if context is not None:
            log.debug("Postprocessing YAML data")
            from .tags import postprocess
            data = postprocess(data, context)
        else:
            log.debug("Skipped postprocessing of YAML data")
    except Exception as e:
        log.debug("YAML source causing the exception is %s", str(source))
        raise
    return data


def load_yaml_file(filepath: Union[str, Path], context: Union[Dict, Any] = {}):
    _filepath = find_file(filepath)
    if isinstance(_filepath, Path):
        return load_yaml_string(_filepath, context)
    else:
        raise FileNotFoundError()
