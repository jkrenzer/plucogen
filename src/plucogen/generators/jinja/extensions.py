import re
from typing import Tuple
from jinja2.ext import Extension
from jinja2 import nodes
from logging import getLogger

log = getLogger(__name__)


class YAMLMetadata(Extension):
    separator_re = re.compile(r"\n+---\n*|\n+\.\.\.\n*")

    def __init__(self, environment):
        super().__init__(environment)
        self._metadata = dict()
        environment.globals["Metadata"] = self._metadata

    def _load_mixed_string(self, string) -> Tuple[dict, str]:
        from ruamel.yaml import YAML, scanner, constructor

        data = dict()
        if re.search(self.separator_re, string):
            content = str()
            sections = re.split(self.separator_re, string)
            for section in sections:
                try:
                    yaml = YAML(typ="safe", pure=True)
                    local_data = yaml.load(section)
                    if not isinstance(local_data, dict):
                        log.info(
                            "Ignored non-map meta-data:\n\n%s\n\n", str(local_data)
                        )
                    else:
                        data |= local_data
                except (scanner.ScannerError, constructor.ConstructorError) as e:
                    log.debug("Collecting non-yaml content: \n%s\n", section)
                    content += section
            log.debug("Loaded data: \n%s\n", str(data))
        else:
            log.debug("No mixed data to load")
            content = string
        return (data, content)

    def preprocess(self, source, name, filename=None) -> str:
        log.debug("Preprocessing template %s (file: %s)", str(name), str(filename))
        data, content = self._load_mixed_string(str(source))
        self._metadata |= data
        log.debug("Preprocessing yielded following source:\n%s\n", content)
        return content
