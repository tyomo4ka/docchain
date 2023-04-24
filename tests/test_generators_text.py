from docchain.specs import TextDocumentSpec
from docchain.generators.text import TextGenerator
from docchain.documents import Format
from langchain.llms.fake import FakeListLLM


def test_generator_text():
    llm = FakeListLLM(responses=["Intro section text.", "Description section text."])
    generator = TextGenerator(llm=llm)
    spec = TextDocumentSpec.parse_obj(
        {
            "document_title": "Demo",
            "document_filename": "TEST.txt",
            "document_name": "TEST",
            "document_description": "Policy Disclosure Statement",
            "sections": [
                {
                    "title": "Intro",
                    "description": "Document Intro",
                },
                {
                    "title": "Description",
                    "description": "Document Description",
                },
            ],
        }
    )
    doc = generator.build_document(spec)

    assert doc.format == Format.text
    assert doc.title == "Demo"
    assert (
        doc.text
        == """Demo

Intro

Intro section text.

Description

Description section text.

"""
    )
