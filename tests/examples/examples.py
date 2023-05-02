from logging import getLogger

from docchain.documents import Document, Section
from docchain.specs import Spec
from docchain.middleware.base import AbstractMiddleware

logger = getLogger(__name__)


class AddTitleSectionMiddleware(AbstractMiddleware):
    def doc_pass(self, document: Document):
        document.sections.append(
            Section(
                title="test document_title", summary="test summary", text="test text"
            )
        )

        document.text = document.sections[0].text

        return document


def mark_as_draft(build_document):
    def run(spec: Spec):
        logger.debug("mark_as_draft spec pass")

        # This modifies the Spec
        spec.document_title = f"WIP: {spec.document_title}"
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
