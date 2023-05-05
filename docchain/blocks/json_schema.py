import json

from langchain.llms.base import BaseLLM
from langchain.prompts import PromptTemplate
from pydantic import BaseModel

from ..output_parsers import JSONSchemaOutputParser
from .base import BaseBlock


class JSONSchemaBlockModel(BaseModel):
    title: str
    description: str


class JSONSchemaBlock(BaseBlock):
    model = JSONSchemaBlockModel

    def create_prompt(self, llm: BaseLLM, **kwargs):
        parser = JSONSchemaOutputParser()
        return PromptTemplate(
            template="""Give me JSON Schema for {title}.
{description}
{format_instructions}
            """,
            output_parser=parser,
            input_variables=["title", "description"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

    def transform_result(self, result: str) -> any:
        return json.loads(result)
