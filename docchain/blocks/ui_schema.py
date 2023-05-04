import json

from langchain.chains import LLMChain
from langchain.llms.base import BaseLLM
from langchain.prompts import PromptTemplate

from ..documents import Document
from ..output_parsers import UISchemaOutputParser
from .base import BaseBlock


class UISchemaBlock(BaseBlock):
    def __init__(self, key: str, /, json_schema: str):
        super().__init__(key)
        self.json_schema = json_schema

    @staticmethod
    def create_chain(llm: BaseLLM):
        parser = UISchemaOutputParser()
        default_prompt = PromptTemplate(
            template="""Generate form configuration for the following JSON Schema.

{json_schema}
{format_instructions}
            """,
            output_parser=parser,
            input_variables=["json_schema"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        llm_chain = LLMChain(prompt=default_prompt, llm=llm)

        return llm_chain

    def __call__(self, document: Document, llm: BaseLLM, **kwargs) -> any:
        llm_chain = self.create_chain(llm)
        result = llm_chain.run(
            json_schema=self.json_schema.format(**document.context),
        )

        return json.loads(result)
