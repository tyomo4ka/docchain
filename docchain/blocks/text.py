from langchain.llms.base import BaseLLM
from langchain.prompts import PromptTemplate
from pydantic import BaseModel

from ..documents import Document
from .base import BaseBlock


class TextBlockModel(BaseModel):
    title: str
    description: str = ""


class TextBlock(BaseBlock):
    model = TextBlockModel

    def create_prompt(self, document: Document, llm: BaseLLM, **kwargs):
        return PromptTemplate(
            template="""
        Write {title} section for {document_title} document.

        {description}
        """,
            input_variables=[
                "title",
                "description",
            ],
            partial_variables={
                "document_title": document.title,
            },
        )
