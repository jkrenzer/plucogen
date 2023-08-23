from abc import ABC, abstractmethod
from logging import getLogger
from typing import Any, Union, List, Dict
from ruamel.yaml.constructor import ConstructorError, BaseConstructor
from jsonschema import validate, Draft202012Validator, ValidationError

import json

from . import get_yaml_instance, yaml_object

log = getLogger(__name__)

yaml = get_yaml_instance()


@yaml_object(yaml)
class Tag(ABC):
    yaml_tag = None

    json_schema = None

    @classmethod
    def get_yaml_tag(cls):
        return cls.yaml_tag or ("!" + cls.__name__)

    @classmethod
    def get_json_schema(cls):
        return cls.json_schema

    @classmethod
    def register_path(cls, path: List[Union[str, int]], kind=None):
        yaml.resolver.add_path_resolver(cls.get_yaml_tag(), path, kind)

    @classmethod
    def validate_data(cls, data: Union[List, Dict, Any], logging=True):
        json_schema = cls.get_json_schema()
        if json_schema:
            try:
                validate(instance=data, schema=json.loads(json_schema))
            except ValidationError as e:
                if logging:
                    log.exception(
                        "YAML json-schema validation for tag %s (python class %s) failed!",
                        cls.yaml_tag,
                        cls.__name__,
                    )
                raise


@yaml_object(yaml)
class Include(Tag):
    yaml_tag = "!include"

    json_schema = """
    {
        "$schema": "https://json-schema.org/draft/2020-12/schema#",
        "$ref": "#/definitions/Include",
        "definitions": {
            "Include": {
                "type": "object",
                "additionalProperties": false,
                "properties": {
                    "file": {
                        "type": "string"
                    },
                    "select": {
                        "type": "string"
                    },
                    "required": {
                        "type": "boolean"
                    }
                },
                "required": [
                    "file"
                ],
                "title": "Include"
            }
        }
    }
    """

    def __init__(self, file, select=None, required=True):
        self.file = file
        self.required = required
        self.select = select

    @classmethod
    def from_data(cls, data):
        from .yaml import load_yaml_file

        filepath = data.get("file", None)
        select_path = data.get("select", None)
        if filepath is not None:
            try:
                log.info("Including contents of file %s", str(filepath))
                data = load_yaml_file(filepath, None)
            except FileNotFoundError as e:
                if not data.get("required", True):
                    log.info(
                        "Include file %s was not found and thus skipped!", filepath
                    )
                else:
                    log.error("Required include file %s was not found!", filepath)
                    raise
        if select_path is not None:
            log.info("Processing selection path %s", select_path)
            select_list = [t for s in select_path.split("/") for t in s.split(".")]
            try:
                for index in select_list:
                    if isinstance(data, list):
                        data = data[int(index)]
                    else:
                        data = data[index]
            except KeyError as e:
                if not data.get("required", True):
                    log.info(
                        "Selected data path %s was not found in include file %s and thus skipped!",
                        select_path,
                        filepath,
                    )
                else:
                    log.error(
                        "Required selected data path %s in include file %s was not found!",
                        select_path,
                        filepath,
                    )
                    raise
        return data

    @classmethod
    def from_yaml(cls, constructor, node):
        # Generate data dict
        data = constructor.construct_mapping(node, deep=True)
        # Validate against schema
        cls.validate_data(data)
        return cls.from_data(data)


class Postprocess(Tag):
    @abstractmethod
    def postprocess(self, data, context, path: list):
        pass


def postprocess(data: Union[dict, list, Any], context: dict = {}, path=[]):
    if isinstance(data, list):
        for num, elem in enumerate(data):
            path.append(num)
            postprocess(elem, context, path)
    elif isinstance(data, dict):
        for key in data:
            path.append(key)
            val = data[key]
            if isinstance(val, Postprocess):
                data[key] = val.postprocess(data, context, path)
            postprocess(data[key], context, path)
    return data


@yaml_object(yaml)
class Template(Postprocess):
    yaml_tag = "!template"

    json_schema = """
    {
        "$schema": "https://json-schema.org/draft/2020-12/schema#",
        "$ref": "#/definitions/Template",
        "definitions": {
            "Template": {
                "anyOf": [
                    {
                        "$ref": "#/definitions/StringTemplate"
                    },
                    {
                        "$ref": "#/definitions/FileTemplate"
                    }
                ]
            },
            "StringTemplate": {
                "type": "string"
            },
            "FileTemplate": {
                "type": "object",
                "additionalProperties": false,
                "properties": {
                    "file": {
                        "type": "string"
                    },
                    "required": {
                        "type": "boolean"
                    }
                },
                "required": [
                    "file"
                ],
                "title": "Template"
            }
        }
    }
    """

    data = {}
    search_paths = []

    def __init__(self, data=data, template=None, text=None, search_paths=search_paths):
        self.data = data
        self.template = template
        self.text = text
        self.search_paths = search_paths

    def __str__(self):
        from plucogen.generators.jinja.render import render

        return render(
            data=self.data,
            text=self.text,
            template=self.template,
            search_paths=self.search_paths,
        )

    def postprocess(self, data, context, path):
        self.data = data
        self.search_paths = context.get("search_paths", [])
        return self.to_data()

    def to_data(self):
        return yaml.load(str(self))

    @classmethod
    def from_yaml(cls: "Template", constructor: BaseConstructor, node):
        if node.id == "scalar":
            content = str(node.value)
        else:
            content = constructor.construct_mapping(node)
        cls.validate_data(content)  # TODO Get validation to work
        obj = cls()
        if isinstance(content, str):
            obj.text = content
        elif isinstance(content, dict):
            obj.template = content.get("file", "")
        return obj
