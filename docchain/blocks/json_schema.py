import json

from langchain.chains import LLMChain
from langchain.llms.base import BaseLLM
from langchain.prompts import PromptTemplate

from ..documents import Document
from ..output_parsers import JSONSchemaOutputParser
from .base import BaseBlock


class JSONSchemaBlock(BaseBlock):
    def __init__(self, key: str, /, title: str, description: str):
        super().__init__(key)
        self.title = title
        self.description = description

    @staticmethod
    def create_chain(llm: BaseLLM):
        parser = JSONSchemaOutputParser()
        default_prompt = PromptTemplate(
            template="""Give me JSON Schema for {section_name}.
{description}
{format_instructions}
            """,
            output_parser=parser,
            input_variables=["section_name", "description"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        llm_chain = LLMChain(prompt=default_prompt, llm=llm)

        return llm_chain

    def __call__(self, document: Document, llm: BaseLLM, **kwargs) -> any:
        llm_chain = self.create_chain(llm)
        result = llm_chain.run(
            section_name=self.title.format(**document.context),
            description=self.description.format(**document.context),
        )

        return json.loads(result)
