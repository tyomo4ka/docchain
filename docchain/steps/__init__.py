"""
Defines reusable builder steps.
Steps can be implemented as a class if required more complex logic or as functions for simpler use.

Class: extend AbstractStep.

See an example of Function step below.


    from docchain.specs import BaseSpec


    def mark_as_draft(build_document):
        def run(spec: BaseSpec):
            # Modify Spec
            spec.document_title = f"WIP: {spec.document_title}"
            document = build_document(spec)
            # Modify Doc
            document.title += " (Draft)"

            return document

        return run
"""
