from jinja2 import Environment as BasicEnvironment, FileSystemLoader
from jinja2.environment import Template
from plucogen.logging import getLogger
from pathlib import PurePath, Path
from os import path
from typing import Union, Dict, List

from plucogen.handlers.yaml import load_yaml_file
from plucogen.file import set_search_paths

log = getLogger(__name__)


class Environment(BasicEnvironment):
    """Jinja2 Environment with our defaults set"""

    default_extensions = ["plucogen.generators.jinja.extensions.YAMLMetadata"]

    def __init__(self, *args, extensions=default_extensions, **kwargs):
        log.debug("Contructing Jinja2 Environment with defaults")
        return super().__init__(*args, extensions=extensions, **kwargs)


def process_template(template, environment, data: Dict = {}):
    """Parse template to search for referenced files"""
    if isinstance(template, str):
        log.debug("Converting source string to template")
        template = environment.from_string(template)
    return template.render(data)


def render(
    data: Union[str, Dict, List],
    template: Union[str, Template, None] = None,
    text: Union[str, None] = None,
    search_paths: List[Union[Path, str]] = [],
):
    """Generate result text from Jinja2 templates and YAML data files"""
    set_search_paths(search_paths)
    if template is not None and text is not None:
        raise TypeError(
            "render can only work on a template(-file) or a text. Do not supply both!"
        )
    if template is None and text is None:
        raise TypeError(
            "supply either a template/template-file-path or a text to render!"
        )
    log.debug(
        "Reading files from %s",
        ", ".join([p if isinstance(p, str) else str(p) for p in search_paths]),
    )
    environment = Environment(loader=FileSystemLoader(search_paths), autoescape=None)
    if isinstance(data, str):
        data = load_yaml_file(data, {"search_paths": search_paths})
    if isinstance(data, Dict):
        pass
    else:
        # TODO Do we want this?
        data = {"Data": data}
    if template is not None:
        if isinstance(template, str):
            template = environment.get_template(template)
    else:
        template = text
    return process_template(template=template, environment=environment, data=data)


def render_files(
    output_input_map: Dict[Union[str, None], List[str]],
    data: Union[str, Dict, List],
    search_paths: List[Union[Path, str]],
):
    """Generate files from Jinja2 templates and YAML data files"""
    for output, inputs in output_input_map.items():
        template_file = path.abspath(inputs[0])
        template_path = PurePath(template_file)
        _search_paths = [str(template_path.parent), "/"] + search_paths
        log.debug("Reading files from %s", ", ".join(str(_search_paths)))
        log.debug("Reading %s", str(template_path))
        # Get data, metadata and content
        rendered_file = render(
            template=template_file, search_paths=_search_paths, data=data
        )
        if isinstance(output, str):
            with open(output, "w") as file_descriptor:
                file_descriptor.write(rendered_file)
                return 0
        else:
            return rendered_file


def main(options):
    """Call from argparse options from the CLI, unittests or extension programs"""
    return render_files(
        output_input_map={options.output: options.input},
        search_paths=options.search_paths,
        data=options.data,
    )


from plucogen.generators import generatorParsers

renderSubParser = generatorParsers.add_parser(
    "jinja", help="render Jinja template files with data"
)  # type: ignore
renderSubParser.set_defaults(func=main)

renderSubParser.add(
    "-d", "--data", required=True, help="data file to use"  # type: ignore
)
renderSubParser.add("-m", "--metadata", help="metadata file to load")  # type: ignore
renderSubParser.add(
    "-s",
    "--search-path",
    action="append",
    default=["./"],
    dest="search_paths",
    metavar="SEARCH_PATH",  # type: ignore
    help="""Additional paths to search for templates. Can occure
           multiple times.""",
)
renderSubParser.add(
    "-o",
    "--output",
    required=False,  # type: ignore
    help="filepath for the output-file.",
)
renderSubParser.add("input", nargs=1, help="template file to process")  # type: ignore
