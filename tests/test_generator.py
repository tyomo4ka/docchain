import os

import pytest
from langchain.llms.fake import FakeListLLM
from pydantic import BaseModel

from docchain.blocks import PydanticBlock
from docchain.documents import Document, Format
from docchain.exceptions import DocumentGenerationError
from docchain.generator import Generator
from docchain.specs import Spec
from tests.conftest import override_settings
from tests.examples.examples import (
    AddSectionMiddleware,
    mark_as_draft,
    throws_exception,
)


class ModelForTests(BaseModel):
    title: str
    description: str


def test_basic_document_builder():
    document_builder = Generator(
        middleware=(
            mark_as_draft,
            AddSectionMiddleware,
        ),
        llm=FakeListLLM(responses=[]),
    )
    spec = Spec(title="Test title")
    document: Document = document_builder(spec)
    assert document.title == "WIP: Test title (Draft)"
    assert len(document.res.values()) == 1
    assert list(document.res.values())[0].title == "test document_title"


def test_exception_handling(tmpdir):
    with override_settings(fs_workspace=tmpdir, debug=True):
        document_builder = Generator(
            middleware=(throws_exception,),
            llm=FakeListLLM(responses=[]),
        )
        spec = Spec(title="Test")
        with pytest.raises(DocumentGenerationError):
            document_builder(spec)

        file = tmpdir.join("failed/Test")
        assert os.path.exists(file)


def test_generator_pydantic():
    llm = FakeListLLM(
        responses=[
            '{"title": "Item 1", "description": "Item section text 1"}',
            '{"title": "Item 2", "description": "Item section text 2"}',
            '{"title": "Item 1", "description": "Item section text 1"}',
            '{"title": "Item 2", "description": "Item section text 2"}',
        ]
    )
    generator = Generator(llm=llm)
    spec = Spec(
        title="Test document",
        name="TD",
        description="Test description",
        blocks=[
            PydanticBlock(
                "Item_1",
                model=ModelForTests,
                title="Item 1",
            ),
            PydanticBlock(
                "Item_2",
                title="Item 2",
                model=ModelForTests,
            ),
        ],
    )

    doc = generator.build_document(spec)

    assert doc.format == Format.json
    assert doc.title == "Test document"
    assert (
        doc.text
        == """{
    "Item_1": {
        "title": "Item 1",
        "description": "Item section text 1"
    },
    "Item_2": {
        "title": "Item 2",
        "description": "Item section text 2"
    }
}"""
    )

    spec.fmt = Format.yaml
    doc = generator.build_document(spec)
    assert (
        doc.text
        == """Item_1:
    description: Item section text 1
    title: Item 1
Item_2:
    description: Item section text 2
    title: Item 2
"""
    )


def test_nested_key():
    generator = Generator(
        llm=FakeListLLM(
            responses=[
                '{"title": "Title", "description": "Description"}',
            ]
        )
    )

    spec = Spec(
        title="Test document",
        name="TD",
        description="Test description",
        blocks=[
            PydanticBlock(
                "nested.section",
                title="Test section",
                model=ModelForTests,
            ),
        ],
    )

    doc = generator.build_document(spec)

    assert doc.format == Format.json
    assert doc.title == "Test document"
    assert (
        doc.text
        == """{
    "nested": {
        "section": {
            "title": "Title",
            "description": "Description"
        }
    }
}"""
    )
