from enum import Enum

from pydantic import BaseModel, Field
from pathlib import Path


class PydanticFormat(str, Enum):
    json = "json"
    yaml = "yaml"


class Format(str, Enum):
    text = "text"


class Section(BaseModel):
    """
    Section is a composite block for Documents.
    """

    title: str
    summary: str | None = None
    text: str = Field(default="")


class Document(Section):
    """
    Document consist of Sections.
    It should support the same behaviour as section though so documents can be
    included in other documents.
    """

    sections: list[Section] = Field(default=[])
    format: Format | PydanticFormat = Format.text
    filename: Path = Field(default=None)
    stats: dict[str, int | float] = Field(default={})
