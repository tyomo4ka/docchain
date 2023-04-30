from docchain.documents import PydanticFormat
from docchain.generators.pydantic import PydanticGenerator
from langchain.llms.fake import FakeListLLM
from pydantic import BaseModel

from docchain.specs import PydanticDocumentSpec, ModelSectionSpec, JSONSchemaSectionSpec


class TestModel(BaseModel):
    title: str
    description: str


def test_generator_pydantic():
    llm = FakeListLLM(
        responses=[
            '{"title": "Item 1", "description": "Item section text 1"}',
            '{"title": "Item 2", "description": "Item section text 2"}',
            '{"title": "Item 1", "description": "Item section text 1"}',
            '{"title": "Item 2", "description": "Item section text 2"}',
        ]
    )
    generator = PydanticGenerator(llm=llm)
    spec = PydanticDocumentSpec(
        document_title="Test document",
        document_name="TD",
        document_description="Test description",
        sections=[
            ModelSectionSpec(
                section_name="Item 1",
                key="Item_1",
                document_schema=TestModel,
            ),
            ModelSectionSpec(
                section_name="Item 2",
                key="Item_2",
                document_schema=TestModel,
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
    generator = PydanticGenerator(
        llm=FakeListLLM(
            responses=[
                '{"title": "Title", "description": "Description"}',
            ]
        )
    )

    spec = PydanticDocumentSpec(
        document_title="Test document",
        document_name="TD",
        document_description="Test description",
        sections=[
            ModelSectionSpec(
                section_name="Test section",
                key="nested.section",
                document_schema=TestModel,
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
    generator = PydanticGenerator(
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
    spec = PydanticDocumentSpec(
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
