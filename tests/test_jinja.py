from unittest.mock import patch

from langchain.llms.fake import FakeListLLM

from docchain.blocks import JSONSchemaBlock, UISchemaBlock
from docchain.generator import Generator
from docchain.specs import Spec


def record_and_call(original_method: callable, calls: list):
    def wrapper(self, *args, **kwargs):
        calls.append((self, args, kwargs))

        return original_method(self, *args, **kwargs)

    return wrapper


recorded_calls = []


@patch(
    "langchain.llms.fake.FakeListLLM._call",
    new=record_and_call(FakeListLLM._call, recorded_calls),
)
def test_using_jinja_templates():
    llm = FakeListLLM(
        responses=[
            """{
    "$schema": "https://json-schema.org/draft-2020-12/schema",
    "type": "object",
    "properties": {
        "firstName": {
            "type": "string"
        }
    },
    "required": [
        "firstName"
    ]
}
""",
            """{
    "firstName": {
        "ui:autofocus": true
    }
}
""",
        ]
    )
    generator = Generator(llm=llm)
    spec = Spec(
        title="Test",
        name="TD",
        description="Test description",
        blocks=[
            JSONSchemaBlock(
                "person_details_schema",
                title="Validate person details",
                description="Include first name, last name, and age.",
            ),
            UISchemaBlock(
                "person_details_ui_schema",
                json_schema="{{ person_details_schema | tojson }}",
            ),
        ],
    )

    doc = generator.build_document(spec)
    assert (
        doc.text
        == """{
    "person_details_schema": {
        "$schema": "https://json-schema.org/draft-2020-12/schema",
        "type": "object",
        "properties": {
            "firstName": {
                "type": "string"
            }
        },
        "required": [
            "firstName"
        ]
    },
    "person_details_ui_schema": {
        "firstName": {
            "ui:autofocus": true
        }
    }
}"""
    )
    # ensure json schema was rendered correctly
    assert (
        """"properties": {"firstName": {"type": "string"}}""" in recorded_calls[1][1][0]
    )
