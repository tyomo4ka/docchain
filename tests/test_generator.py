import os
import pytest

from docchain.documents import Format, Document
from docchain.generator import Generator
from docchain.exceptions import DocumentGenerationError
from langchain.llms.fake import FakeListLLM
from pydantic import BaseModel
from docchain.blocks.pydantic import PydanticBlock
from docchain.blocks.json_schema import JSONSchemaBlock

from tests.examples.examples import (
    AddSectionMiddleware,
    mark_as_draft,
    throws_exception,
)
from docchain.specs import Spec


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


def test_exception_handling():
    document_builder = Generator(
        middleware=(throws_exception,),
        llm=FakeListLLM(responses=[]),
    )
    spec = Spec(title="Test")
    with pytest.raises(DocumentGenerationError):
        document_builder(spec)

    assert os.path.exists(".docchain/failed/Test")


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


def test_jsonschema():
    generator = Generator(
        llm=FakeListLLM(
            responses=[
                """{
    "$schema": "http://json-schema.org/draft-2020-12/schema",
    "type": "object",
    "properties": {
        "firstName": {
            "type": "string"
        },
        "lastName": {
            "type": "string"
        },
        "age": {
            "type": "integer"
        }
    },
    "required": [
        "firstName",
        "lastName",
        "age"
    ]
}
""",
            ]
        )
    )
    spec = Spec(
        title="Test document",
        name="TD",
        description="Test description",
        blocks=[
            JSONSchemaBlock(
                "person_details_schema",
                title="Validate person details",
                description="Include first name, last name, and age.",
            ),
        ],
    )

    doc = generator.build_document(spec)
    assert (
        doc.text
        == """{
    "person_details_schema": {
        "$schema": "http://json-schema.org/draft-2020-12/schema",
        "type": "object",
        "properties": {
            "firstName": {
                "type": "string"
            },
            "lastName": {
                "type": "string"
            },
            "age": {
                "type": "integer"
            }
        },
        "required": [
            "firstName",
            "lastName",
            "age"
        ]
    }
}"""
    )
