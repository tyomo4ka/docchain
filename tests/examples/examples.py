from logging import getLogger

from docchain.documents import Document, Section
from docchain.middleware.base import AbstractMiddleware
from docchain.specs import Spec

logger = getLogger(__name__)


class AddSectionMiddleware(AbstractMiddleware):
    def doc_pass(self, document: Document):
        document.res["test"] = Section(
            title="test document_title", summary="test summary", text="test text"
        )

        return document


def mark_as_draft(build_document):
    def run(spec: Spec):
        logger.debug("mark_as_draft spec pass")

        # This modifies the Spec
        spec.title = f"WIP: {spec.title}"
        document = build_document(spec)
        logger.debug("mark_as_draft doc pass")

        # This modifies the Doc
        document.title += " (Draft)"

        return document

    return run


def throws_exception(build_document):
    def run(spec: Spec):
        build_document(spec)
        # Exception is raised after document generation.
        raise NotImplementedError("This will be converted.")

    return run
