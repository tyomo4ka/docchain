import json
import os
import pickle
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

    @staticmethod
    def format(spec: Spec):
        doc = spec.doc

        match spec.fmt:
            case Format.json:
                formatted = json.dumps(doc.res, indent=4)
            case Format.yaml:
                formatted = yaml.dump(doc.res, indent=4)
            case Format.text:
                formatted = [f"{key}\n\n{value}" for key, value in doc.res]
            case _:
                raise DocumentGenerationError(f"Unknown format: {spec.fmt}")

        return formatted

    def _build_document(self, spec: Spec) -> Document:
        try:
            document = self.handler(spec)
        except Exception as exc:
            if conf.debug:
                logger.debug(spec.doc.res)

            self._maybe_save_wip(spec)
            self._maybe_save_snapshot(spec)

            raise DocumentGenerationError("Document generation failed") from exc

        return document

    def _maybe_save_wip(self, spec: Spec):
        """
        Save document in progress to workspace.
        """
        if spec.doc and spec.doc.filename:
            fs = conf.fs
            fname = f"{conf.fs_workspace}/{spec.doc.filename}.wip"
            fs.makedirs(os.path.dirname(fname), exist_ok=True)
            with fs.open(fname, mode="w") as file:
                file.write(self.format(spec))

    @staticmethod
    def _maybe_save_snapshot(spec: Spec):
        """
        Pickle document snapshot in the workspace.
        """
        if spec.doc and spec.doc.filename:
            fs = conf.fs
            fname = f"{conf.fs_workspace}/{spec.doc.filename}.snapshot"
            fs.makedirs(os.path.dirname(fname), exist_ok=True)
            with fs.open(fname, mode="wb") as file:
                file.write(pickle.dumps(spec.doc))

    @staticmethod
    def _maybe_restore_from_snapshot(spec: Spec) -> Document | None:
        """
        Restore document from snapshot in the workspace.
        """
        if spec.filename:
            fs = conf.fs
            fname = f"{conf.fs_workspace}/{spec.filename}.snapshot"
            if fs.exists(fname):
                with fs.open(fname, mode="rb") as file:
                    doc = pickle.loads(file.read())
                return doc

        return None

    def __call__(self, spec: Spec) -> Document:
        # As generator can optionally modify spec, ensure it's working with a copy
        spec_copy = deepcopy(spec)
        doc = self._build_document(spec_copy)

        return doc

    def build_document(self, spec: Spec) -> Document:
        doc = self._maybe_restore_from_snapshot(spec)
        if not doc:
            doc = Document(
                title=spec.title,
                filename=spec.filename,
                format=spec.fmt,
                res={},
            )
        spec.doc = doc

        # maybe remove wip and snapshot files
        fs = conf.fs
        wip_fname = f"{conf.fs_workspace}/{spec.filename}.wip"
        fs.exists(wip_fname) and fs.rm(wip_fname)
        snapshot_fname = f"{conf.fs_workspace}/{spec.filename}.snapshot"
        fs.exists(snapshot_fname) and fs.rm(snapshot_fname)

        for block in spec.blocks:
            if block.key in doc.res:
                continue

            res = block(
                document=doc,
                llm=self.llm,
            )
            set_nested_val(doc.res, block.key, res)

        doc.text = self.format(spec)

        return doc
