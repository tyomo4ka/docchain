from enum import Enum
from typing import Any

from pydantic import BaseModel, Field
from pathlib import Path


class Format(str, Enum):
    json = "json"
    yaml = "yaml"
    text = "text"


class Section(BaseModel):
    """
    Section is a composite block for Documents.
    """

    title: str = Field(default="")
    summary: str | None = None
    text: str = Field(default="")


class Document(Section):
    """
    Document consist of Sections.
    It should support the same behaviour as section though so documents can be
    included in other documents.
    """

    res: dict[str, Any]
    format: Format = Format.text
    filename: Path = Field(default=None)
    stats: dict[str, int | float] = Field(default={})
