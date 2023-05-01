from pathlib import Path
from pydantic import BaseModel, Field
from .documents import Document, PydanticFormat


class BaseSectionSpec(BaseModel):
    title: str = Field(
        default="", description="The title of the section within the document."
    )
    description: str = Field(
        default="", description="A brief description of the section."
    )
    key: str = Field(
        regex="[a-zA-Z0-9_\\-\\.]{1,100}",
        description="A unique string key for the section. Must be unique within the document. "
        "Dot in the key represents a nested section.",
    )


class TextSectionSpec(BaseSectionSpec):
    pass


class JSONSchemaSectionSpec(BaseSectionSpec):
    pass


class ModelSectionSpec(BaseSectionSpec):
    document_schema: type[BaseModel] = Field(
        description="A Pydantic model representing the schema for the section."
    )


class Spec(BaseModel):
    document_title: str = Field(description="The title of the document.")
    filename: Path = Field(
        default=None,
        description="The filename of the document as a Path object. Defaults to None.",
    )
    document_name: str = Field(default="", description="The name of the document.")
    doc: "Document" = Field(
        default=None,
        description="The Document object associated with the specification. Defaults to None.",
    )
    format: PydanticFormat = Field(
        default=PydanticFormat.json,
        description="The format of the document as a PydanticFormat object. Defaults to json.",
    )
    sections: list[BaseSectionSpec] = Field(
        default=[],
        description="A list of objects representing the sections within the document.",
    )
