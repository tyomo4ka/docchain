import json
import re

from langchain.schema import BaseOutputParser, OutputParserException

FORMAT_INSTRUCTIONS = (
    "Give me valid UI schema for the latest version of react-jsonschema-form library."
)


class UISchemaOutputParser(BaseOutputParser):
    def parse(self, text: str) -> dict:
        try:
            match = re.search(
                "{.*}", text.strip(), re.MULTILINE | re.IGNORECASE | re.DOTALL
            )
            json_str = ""
            if match:
                json_str = match.group()

            json_object = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise OutputParserException(f"Failed to parse json. Completion {text}: {e}")

        return json_object

    def get_format_instructions(self) -> str:
        return FORMAT_INSTRUCTIONS

    @property
    def _type(self) -> str:
        return "ui_schema"
