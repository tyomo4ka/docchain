import os

from langchain.prompts import PromptTemplate
from pydantic import BaseModel

from docchain.blocks import BaseBlock


class TestBlockModel(BaseModel):
    title: str


class RaisesExceptionOnFirstCallBlock(BaseBlock):
    """
    This is a testing block. It is used to test restarts of the document generation.
    It raises an exception on the first call only.
    """

    model = TestBlockModel
    calls_count = {}

    def __init__(self, key, /, **kwargs):
        super().__init__(key, **kwargs)

    def create_prompt(self, **kwargs):
        return PromptTemplate(
            template="This is a testing block: {title}.",
            input_variables=["title"],
        )

    def __call__(self, **kwargs) -> any:
        test_func = os.getenv("PYTEST_CURRENT_TEST")
        print(test_func)
        self.calls_count.setdefault(test_func, 0)
        self.calls_count[test_func] = self.calls_count[test_func] + 1
        if self.calls_count[test_func] == 1:
            raise Exception("Called first time.")

        return super().__call__(**kwargs)
