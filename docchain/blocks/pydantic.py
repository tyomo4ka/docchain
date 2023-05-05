import json

from langchain.llms.base import BaseLLM
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from pydantic import BaseModel

from .base import BaseBlock


class PydanticBlockModel(BaseModel):
    title: str
    model: type[BaseModel]
    description: str = ""


class PydanticBlock(BaseBlock):
    model = PydanticBlockModel

    def create_prompt(self, llm: BaseLLM, **kwargs):
        parser = PydanticOutputParser(pydantic_object=self.model)
        return PromptTemplate(
            template="""
        Write {title} section of configuration file for {description}.

        {format_instructions}
        """,
            input_variables=["title", "description"],
            output_parser=parser,
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

    def transform_result(self, result: str) -> any:
        return json.loads(result)
