import json
import re

import jsonschema
from jsonschema import Draft202012Validator
from langchain.schema import BaseOutputParser, OutputParserException

FORMAT_INSTRUCTIONS = (
    "Give me result as json schema draft 2020-12. Use camel case for fields names. "
    "Be as concise as possible, use short names, reuse names where possible. "
    "Do not omit anything or use ..."
)


def is_valid_json_schema(schema: dict) -> tuple[bool, list[str] | None]:
    metaschema = Draft202012Validator.META_SCHEMA
    validator = jsonschema.Draft202012Validator(metaschema)
    errors = []

    for error in validator.iter_errors(schema):
        errors.append(str(error))

    if errors:
        return False, errors
    else:
        return True, None


class JSONSchemaOutputParser(BaseOutputParser):
    def parse(self, text: str) -> dict:
        try:
            # Finds what looks like the first json object in the text
            match = re.search(
                "{.*}", text.strip(), re.MULTILINE | re.IGNORECASE | re.DOTALL
            )
            json_str = ""
            if match:
                json_str = match.group()

            json_object = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise OutputParserException(f"Failed to parse json. Completion {text}: {e}")

        is_valid, errors = is_valid_json_schema(json_object)
        if not is_valid:
            raise OutputParserException(
                f"Invalid json schema: {errors}. Completion: {text}"
            )

        return json_object

    def get_format_instructions(self) -> str:
        return FORMAT_INSTRUCTIONS

    @property
    def _type(self) -> str:
        return "json_schema"
