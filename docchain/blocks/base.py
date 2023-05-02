from langchain.llms.base import BaseLLM

from ..documents import Document


class BaseBlock:
    def __init__(self, key, /, **kwargs):
        self.key = key

    def __call__(self, document: Document, llm: BaseLLM):
        raise NotImplementedError()
