import os
from docchain.generator import Generator
from docchain.specs import Spec
from docchain.documents import Document
from .examples.examples import AddTitleSectionMiddleware
from docchain.middleware.save_document import SaveDocumentMiddleware
from .conftest import override_settings
from langchain.llms.fake import FakeListLLM


def test_save_document(tmpdir):
    with override_settings(workspace=tmpdir):
        document_builder = Generator(
            middleware=(
                AddTitleSectionMiddleware,
                SaveDocumentMiddleware,
            ),
            llm=FakeListLLM(responses=[]),
        )
        filename = "test.txt"
        spec = Spec(filename=filename, title="Product description")
        document: Document = document_builder(spec)
        file = tmpdir.join(filename)
        assert document.title == "Product description"
        assert os.path.exists(file)
        assert file.read() == "test text"
