from langchain.llms.fake import FakeListLLM

from docchain.blocks import JSONSchemaBlock, UISchemaBlock
from docchain.generator import Generator
from docchain.specs import Spec


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
                """{
  "firstName": {
    "ui:autofocus": true,
    "ui:emptyValue": "",
    "ui:placeholder": "ui:emptyValue",
    "ui:autocomplete": "family-name"
  },
  "lastName": {
    "ui:autocomplete": "given-name"
  },
  "age": {
    "ui:widget": "updown",
    "ui:title": "Age of person",
    "ui:description": "(earth year)"
  }
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
            UISchemaBlock(
                "person_details_ui_schema",
                json_schema="{person_details_schema}",
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
    },
    "person_details_ui_schema": {
        "firstName": {
            "ui:autofocus": true,
            "ui:emptyValue": "",
            "ui:placeholder": "ui:emptyValue",
            "ui:autocomplete": "family-name"
        },
        "lastName": {
            "ui:autocomplete": "given-name"
        },
        "age": {
            "ui:widget": "updown",
            "ui:title": "Age of person",
            "ui:description": "(earth year)"
        }
    }
}"""
    )
