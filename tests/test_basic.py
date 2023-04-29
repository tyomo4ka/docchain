import os

import pytest

from docchain.documents import Document
from docchain.generators.base import BaseDocumentGenerator
from docchain.specs import Spec
from docchain.exceptions import DocumentGenerationError
from tests.examples.examples import AddTitleSectionStep, mark_as_draft, throws_exception


def test_basic_document_builder():
    document_builder = BaseDocumentGenerator(
        (
            mark_as_draft,
            AddTitleSectionStep,
        )
    )
    spec = Spec(document_title="Test title")
    document: Document = document_builder(spec)
    assert document.title == "WIP: Test title (Draft)"
    assert len(document.sections) == 1
    assert document.sections[0].title == "test document_title"


def test_exception_handling():
    document_builder = BaseDocumentGenerator(steps=[throws_exception])
    spec = Spec(document_title="Test")
    with pytest.raises(DocumentGenerationError):
        document_builder(spec)

    assert os.path.exists(".docchain/failed/Test")
