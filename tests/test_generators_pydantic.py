from docchain.documents import Format, PydanticFormat
from docchain.generators.pydantic import PydanticGenerator
from langchain.llms.fake import FakeListLLM
from pydantic import BaseModel

from docchain.specs import PydanticDocumentSpec, PydanticSectionSpec


def test_generator_pydantic():
    class TestModel(BaseModel):
        title: str
        description: str

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
            PydanticSectionSpec(
                section_name="Item 1",
                key="Item_1",
                document_schema=TestModel,
            ),
            PydanticSectionSpec(
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
