import json

from langchain.chains import LLMChain
from langchain.llms.base import BaseLLM
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel

from .base import BaseBlock


class PydanticBlock(BaseBlock):
    def __init__(
        self, key: str, /, model: type[BaseModel], title: str, description: str = ""
    ):
        super().__init__(key)
        self.model = model
        self.title = title
        self.description = description

    def __call__(self, llm: BaseLLM, **kwargs):
        parser = PydanticOutputParser(pydantic_object=self.model)
        default_prompt = PromptTemplate(
            template="""
        Write {title} section of configuration file for {description}.

        {format_instructions}
        """,
            input_variables=["title", "description"],
            output_parser=parser,
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        llm_chain = LLMChain(prompt=default_prompt, llm=llm)
        result = llm_chain.run(
            title=self.title,
            description=self.description,
        )

        return json.loads(result)
