from .documents import Format
from .blocks.base import BaseBlock
from .documents import Document


class Spec:
    def __init__(
        self,
        title: str = "",
        filename: str = None,
        name: str = "",
        description: str = "",
        fmt: Format = Format.json,
        blocks: list[BaseBlock] | callable = None,
        doc: Document = None,
    ):
        self.title = title
        self.filename = filename
        self.name = name
        self.description = description
        self.fmt = fmt
        self.blocks = blocks or []
        self.doc = doc
