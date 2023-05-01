import os
from docchain.generator import Generator
from docchain.specs import Spec
from docchain.documents import Document
from .examples.examples import AddTitleSectionStep
from docchain.steps.save_document import SaveDocumentStep
from .conftest import override_settings


def test_save_document(tmpdir):
    with override_settings(workspace=tmpdir):
        document_builder = Generator(
            steps=(
                AddTitleSectionStep,
                SaveDocumentStep,
            )
        )
        filename = "test.txt"
        spec = Spec(filename=filename, document_title="Product description")
        document: Document = document_builder(spec)
        file = tmpdir.join(filename)
        assert document.title == "Product description"
        assert os.path.exists(file)
        assert file.read() == "test text"
