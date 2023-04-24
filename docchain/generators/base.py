import os
from collections.abc import Iterable
from copy import deepcopy
from logging import getLogger

from ..exceptions import DocumentGenerationError
from ..specs import Spec
from ..documents import Document
from ..settings import conf

logger = getLogger(__name__)


class BaseDocumentGenerator:
    """
    A base class that defines the framework for building documents.
    The business logic itself can be implemented in reusable steps and in subclasses.
    """

    steps = Iterable[callable]
    handler = None

    def __init__(self, steps: Iterable[callable]):
        self.steps = steps
        handler = self.build_document

        for step in self.steps:
            handler = step(handler)

        self.handler = handler

    def _build_document(self, spec: Spec) -> Document:
        try:
            document = self.handler(spec)
        except Exception as exc:
            if conf.debug:
                if spec.doc:
                    logger.debug(spec.doc)
                    fname = f"{conf.workspace}/failed/{spec.document_title}"
                    os.makedirs(os.path.dirname(fname), exist_ok=True)
                    with open(
                        f"{conf.workspace}/failed/{spec.document_title}", mode="a+"
                    ) as file:
                        file.write(str(spec.doc.dict()))

            raise DocumentGenerationError("Document generation failed") from exc

        return document

    def build_document(self, spec: Spec) -> Document:
        doc = Document(
            filename=spec.filename,
            title=spec.document_title,
            sections=[],
        )
        spec.doc = doc

        return doc

    def __call__(self, spec: Spec) -> Document:
        # As generator can optionally modify spec, ensure it's dealing with a copy
        spec_copy = deepcopy(spec)
        doc = self._build_document(spec_copy)

        return doc
