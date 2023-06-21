from ruamel.yaml import (
    YAML,
    yaml_object,
    MappingNode,
    add_path_resolver,
    add_implicit_resolver,
)


def get_yaml_instance():
    return YAML(typ="safe", pure=True)


from .yaml import load_yaml_file, load_yaml_string

_module_name = __name__
