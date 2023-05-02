from ..documents import Document
from ..settings import conf
from .base import AbstractMiddleware


class SaveDocumentMiddleware(AbstractMiddleware):
    """
    Saves document in the workspace as a text file.
    """

    def doc_pass(self, document: Document):
        if document.filename:
            with open(f"{conf.workspace}/{document.filename}", "w") as file:
                file.write(document.text)
