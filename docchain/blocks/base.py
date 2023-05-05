from langchain.chains import LLMChain
from langchain.llms.base import BaseLLM
from langchain.prompts import BasePromptTemplate
from pydantic import BaseModel

from ..documents import Document


class BaseBlock:
    model: BaseModel = BaseModel

    def __init__(self, key, /, **kwargs):
        self.key = key
        self.config = self.model(**kwargs)

    def create_prompt(self, document: Document, llm: BaseLLM) -> BasePromptTemplate:
        """
        Creates prompt for the give block. Must be implemented in the subclass.
        """
        raise NotImplementedError

    def create_chain(self, document: Document, llm: BaseLLM) -> LLMChain:
        """
        Creates LLMChain for the given block. Could be overridden in the subclass.
        """

        return LLMChain(
            prompt=self.create_prompt(
                document=document,
                llm=llm,
            ),
            llm=llm,
        )

    def get_params(self, document: Document) -> dict:
        """
        Renders params for the given document. Could be overridden in the subclass.
        """
        res = {}
        for key, value in self.config.dict().items():
            if isinstance(value, str):
                value = value.format(**document.context)

            res[key] = value

        return res

    def transform_result(self, result: str) -> any:
        """
        Transforms result of the LLMChain. Could be overridden in the subclass.
        """
        return result

    def __call__(self, document: Document, llm: BaseLLM, **kwargs) -> any:
        llm_chain = self.create_chain(document, llm)
        result = llm_chain.run(**self.get_params(document))

        return self.transform_result(result)
