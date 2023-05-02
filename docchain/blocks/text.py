from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from .base import BaseBlock
from ..settings import conf
from ..documents import Document


class TextBlock(BaseBlock):
    def __init__(self, key: str, /, title: str, description: str):
        super().__init__(key)
        self.title = title
        self.description = description

    def __call_(self, document: Document, **kwargs):
        prompt = PromptTemplate(
            template="""
        Write {section_name} section of {document_name} document.

        {description}
        """,
            input_variables=[
                "section_name",
                "document_name",
                "description",
            ],
        )
        llm_chain = LLMChain(prompt=prompt, llm=conf.default_llm_factory())
        result = llm_chain.run(
            section_name=self.title,
            document_name=document.document_name,
            description=self.description,
        )

        return result
