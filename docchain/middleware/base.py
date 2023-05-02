from ..documents import Document
from ..specs import Spec


class AbstractMiddleware:
    def __init__(self, build_document: callable):
        self.build_document = build_document

    def __call__(self, spec: Spec):
        self.spec_pass(spec)
        document = self.build_document(spec)
        self.doc_pass(document)

        return document

    def spec_pass(self, spec: Spec):
        """
        Can be used to transform spec.
        """
        pass

    def doc_pass(self, doc: Document):
        """
        Can be used to transform generated doc.
        """
        pass
