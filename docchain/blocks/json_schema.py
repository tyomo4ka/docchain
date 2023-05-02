import json

from langchain.chains import LLMChain
from langchain.llms.base import BaseLLM
from langchain.prompts import PromptTemplate

from ..output_parsers.json_schema import JSONSchemaOutputParser
from .base import BaseBlock


class JSONSchemaBlock(BaseBlock):
    def __init__(self, key: str, /, title: str, description: str):
        super().__init__(key)
        self.title = title
        self.description = description

    def __call__(self, llm: BaseLLM, **kwargs) -> any:
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
        result = llm_chain.run(
            section_name=self.title,
            description=self.description,
        )

        return json.loads(result)
