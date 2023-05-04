import json
import os
from collections.abc import Iterable
from copy import deepcopy
from logging import getLogger

import yaml
from langchain.llms.base import BaseLLM

from .documents import Document, Format
from .exceptions import DocumentGenerationError
from .settings import conf
from .specs import Spec
from .utils import set_nested_val

logger = getLogger(__name__)


class Generator:
    def __init__(self, middleware: Iterable[callable] = None, llm: BaseLLM = None):
        self.middleware = middleware or []
        handler = self.build_document
        for step in self.middleware:
            handler = step(handler)

        self.llm = llm or conf.default_llm_factory()
        self.handler = handler

    def _build_document(self, spec: Spec) -> Document:
        try:
            document = self.handler(spec)
        except Exception as exc:
            if conf.debug:
                if spec.doc:
                    logger.debug(spec.doc)

                    fname = f"{conf.workspace}/failed/{spec.title}"
                    os.makedirs(os.path.dirname(fname), exist_ok=True)
                    with open(
                        f"{conf.workspace}/failed/{spec.title}", mode="a+"
                    ) as file:
                        file.write(str(spec.doc.res))

            raise DocumentGenerationError("Document generation failed") from exc

        return document

    def __call__(self, spec: Spec) -> Document:
        # As generator can optionally modify spec, ensure it's dealing with a copy
        spec_copy = deepcopy(spec)
        doc = self._build_document(spec_copy)

        return doc

    def build_document(self, spec: Spec) -> Document:
        doc = Document(
            title=spec.title,
            filename=spec.filename,
            format=spec.fmt,
            res={},
        )
        spec.doc = doc

        for block in spec.blocks:
            res = block(
                document=doc,
                llm=self.llm,
            )
            set_nested_val(doc.res, block.key, res)

        # TODO: move this to a formatter
        match spec.fmt:
            case Format.json:
                doc.text = json.dumps(doc.res, indent=4)
            case Format.yaml:
                doc.text = yaml.dump(doc.res, indent=4)
            case Format.text:
                doc.text = [f"{key}\n\n{value}" for key, value in doc.res]

        return doc
