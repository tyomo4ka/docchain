import os

from langchain.llms.fake import FakeListLLM

from docchain.documents import Document, Format
from docchain.generator import Generator
from docchain.middleware import SaveDocumentMiddleware
from docchain.specs import Spec

from .conftest import override_settings
from .examples.examples import AddSectionMiddleware


def test_save_document(tmpdir):
    with override_settings(fs_workspace=tmpdir):
        document_builder = Generator(
            middleware=(
                AddSectionMiddleware,
                SaveDocumentMiddleware,
            ),
            llm=FakeListLLM(responses=[]),
        )
        filename = "test.txt"

        # Block can also be any callable
        def save_document(*args, **kwargs):
            return "test text"

        save_document.key = "test_key"

        spec = Spec(
            filename=filename,
            fmt=Format.yaml,
            title="Product description",
            blocks=[
                save_document,
            ],
        )
        document: Document = document_builder(spec)
        file = tmpdir.join(filename)
        assert document.title == "Product description"
        assert os.path.exists(file)
        assert file.read() == "test_key: test text\n"
