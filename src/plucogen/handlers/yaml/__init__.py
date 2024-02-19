from ruamel.yaml import (
    YAML,
    MappingNode,
    add_implicit_resolver,
    add_path_resolver,
    yaml_object,
)


def get_yaml_instance():
    return YAML(typ="safe", pure=True)


from .yaml import load_yaml_file, load_yaml_string

_module_name = __name__
