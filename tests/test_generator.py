import os
import pytest

from docchain.documents import PydanticFormat, Document
from docchain.generator import Generator
from docchain.exceptions import DocumentGenerationError
from langchain.llms.fake import FakeListLLM
from pydantic import BaseModel

from tests.examples.examples import AddTitleSectionStep, mark_as_draft, throws_exception
from docchain.specs import Spec, ModelSectionSpec, JSONSchemaSectionSpec


class ModelForTests(BaseModel):
    title: str
    description: str


def test_basic_document_builder():
    document_builder = Generator(
        steps=(
            mark_as_draft,
            AddTitleSectionStep,
        )
    )
    spec = Spec(document_title="Test title")
    document: Document = document_builder(spec)
    assert document.title == "WIP: Test title (Draft)"
    assert len(document.sections) == 1
    assert document.sections[0].title == "test document_title"


def test_exception_handling():
    document_builder = Generator(steps=(throws_exception,))
    spec = Spec(document_title="Test")
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
        document_title="Test document",
        document_name="TD",
        document_description="Test description",
        sections=[
            ModelSectionSpec(
                section_name="Item 1",
                key="Item_1",
                document_schema=ModelForTests,
            ),
            ModelSectionSpec(
                section_name="Item 2",
                key="Item_2",
                document_schema=ModelForTests,
            ),
        ],
    )

    doc = generator.build_document(spec)

    assert doc.format == PydanticFormat.json
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

    spec.format = PydanticFormat.yaml
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
        document_title="Test document",
        document_name="TD",
        document_description="Test description",
        sections=[
            ModelSectionSpec(
                section_name="Test section",
                key="nested.section",
                document_schema=ModelForTests,
            ),
        ],
    )

    doc = generator.build_document(spec)

    assert doc.format == PydanticFormat.json
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
        document_title="Test document",
        document_name="TD",
        document_description="Test description",
        sections=[
            JSONSchemaSectionSpec(
                section_name="Validate person details",
                key="person_details_schema",
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
