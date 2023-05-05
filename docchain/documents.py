from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


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
    filename: Path | None = None
    stats: dict[str, int | float] = Field(default={})
    format: Format = Format.text

    @property
    def context(self):
        res = {
            "doc": {
                "title": self.title,
                "summary": self.summary,
                "text": self.text,
                "filename": self.filename,
            },
        }

        res.update(self.res)

        return res
