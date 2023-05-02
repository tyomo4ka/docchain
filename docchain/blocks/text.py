from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

from ..documents import Document
from ..settings import conf
from .base import BaseBlock


class TextBlock(BaseBlock):
    def __init__(self, key: str, /, title: str, description: str):
        super().__init__(key)
        self.title = title
        self.description = description

    def __call__(self, document: Document, **kwargs):
        prompt = PromptTemplate(
            template="""
        Write {section_name} section of {document_title} document.

        {description}
        """,
            input_variables=[
                "section_name",
                "document_title",
                "description",
            ],
        )
        llm_chain = LLMChain(prompt=prompt, llm=conf.default_llm_factory())
        result = llm_chain.run(
            section_name=self.title,
            document_title=document.title,
            description=self.description,
        )

        return result
