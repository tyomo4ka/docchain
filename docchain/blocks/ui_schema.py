import json

from langchain.llms.base import BaseLLM
from langchain.prompts import PromptTemplate

from ..output_parsers import UISchemaOutputParser
from .base import BaseBlock


class UISchemaBlockModel(BaseBlock.model):
    json_schema: str


class UISchemaBlock(BaseBlock):
    model = UISchemaBlockModel

    def create_prompt(self, llm: BaseLLM, **kwargs) -> PromptTemplate:
        parser = UISchemaOutputParser()

        return PromptTemplate(
            template="""Generate form configuration for the following JSON Schema.

{json_schema}

{format_instructions}
            """,
            output_parser=parser,
            input_variables=["json_schema"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

    def transform_result(self, result: str) -> any:
        return json.loads(result)
