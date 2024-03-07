from typing import Any

from jinja2 import Environment
from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler, GetPydanticSchema
from pydantic_core import CoreSchema, core_schema


class Template(str):
    def evaluate(self, *args, **kwargs) -> str:
        env = Environment()
        return env.from_string(self).render(*args, **kwargs)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls,
            handler(str),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: str(instance)
            ),
        )
