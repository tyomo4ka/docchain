"""
Defines reusable builder middleware.
Steps can be implemented as a class if required more complex logic or as functions for simpler use.

Class: extend AbstractMiddleware.

See an example of Function step below.

    from docchain.specs import Spec


    def mark_as_draft(build_document):
        def run(spec: Spec):
            # Modify Spec
            spec.document_title = f"WIP: {spec.document_title}"
            document = build_document(spec)
            # Modify Doc
            document.title += " (Draft)"

            return document

        return run
"""
from .base import AbstractMiddleware
from .collect_openai_stats import collect_openai_stats
from .save_document import SaveDocumentMiddleware

__all__ = [
    "AbstractMiddleware",
    "collect_openai_stats",
    "SaveDocumentMiddleware",
]
