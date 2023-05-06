import os

import pytest
from langchain.llms.fake import FakeListLLM

from docchain.blocks import TextBlock
from docchain.documents import Format
from docchain.exceptions import DocumentGenerationError
from docchain.generator import Generator
from docchain.specs import Spec
from tests.conftest import override_settings
from tests.testing.blocks import RaisesExceptionOnFirstCallBlock


def test_restart_on_exception(tmpdir):
    with override_settings(fs_workspace=tmpdir, debug=True):
        generator = Generator(
            llm=FakeListLLM(
                responses=[
                    "first item",
                    "second item",
                    "third item",
                ]
            )
        )
        spec = Spec(
            title="Test",
            filename="testing_file",
            fmt=Format.yaml,
            blocks=[
                TextBlock(
                    "first", title="Rendered and saved in the snapshot on first run."
                ),
                RaisesExceptionOnFirstCallBlock(
                    "second", title="Raises exception on first run."
                ),
                TextBlock("third", title="Rendered on second run."),
            ],
        )

        with pytest.raises(DocumentGenerationError):
            generator(spec)

        assert os.path.exists(tmpdir.join(spec.filename + ".wip"))
        assert os.path.exists(tmpdir.join(spec.filename + ".snapshot"))

        assert tmpdir.join(spec.filename + ".wip").read() == "first: first item\n"

        doc = generator(spec)

        assert not os.path.exists(tmpdir.join(spec.filename + ".wip"))
        assert not os.path.exists(tmpdir.join(spec.filename + ".snapshot"))
        assert (
            doc.text == "first: first item\n"
            "second: second item\n"
            "third: third item\n"
        )
