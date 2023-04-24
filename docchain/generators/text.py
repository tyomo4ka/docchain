from collections.abc import Mapping
from collections.abc import Iterable

from langchain.chains import LLMChain
from langchain.llms import BaseLLM
from langchain.prompts import PromptTemplate

from ..specs import TextDocumentSpec, TextSectionSpec
from ..documents import Document, Section
from ..settings import conf
from .base import BaseDocumentGenerator

default_prompt = PromptTemplate(
    template="""
{prefix}

Write {section_name} section of {document_name} document.

{description}

{previous_section}

{suffix}
""",
    input_variables=[
        "prefix",
        "document_name",
        "section_name",
        "description",
        "previous_section",
        "suffix",
    ],
)


class TextGenerator(BaseDocumentGenerator):
    def __init__(
        self,
        steps: Iterable[callable] = None,
        llm: BaseLLM = None,
        prompt: PromptTemplate = None,
        hints: Mapping[str, str] = None,
    ):
        if steps is None:
            steps = []

        super().__init__(steps)

        if hints is None:
            hints = {}

        self.workspace = conf.workspace
        self.llm = llm or conf.default_llm_factory()
        self.llm_chain = LLMChain(prompt=prompt or default_prompt, llm=self.llm)
        self.hints = hints

    def build_document(self, spec: TextDocumentSpec) -> Document:
        doc = Document(
            title=spec.document_title,
            spec=spec,
            text=f"{spec.document_title}\n\n",
        )
        for section_spec in spec.sections:
            include_previous_section = (
                self.hints.get("previous_section", False) and len(doc.sections) > 0
            )
            previous_section = doc.sections[-1].text if include_previous_section else ""
            section = self.build_section(
                spec=spec,
                section_spec=section_spec,
                previous_section=previous_section,
            )
            doc.sections.append(section)
            doc.text += f"{section.title}\n\n{section.text}\n\n"

        return doc

    def build_section(
        self,
        spec: TextDocumentSpec,
        section_spec: TextSectionSpec,
        previous_section: str,
    ):
        text = self.llm_chain.run(
            prefix=self.hints.get("prefix", ""),
            section_name=section_spec.title,
            document_name=spec.document_name,
            description=section_spec.description,
            previous_section=previous_section,
            suffix=self.hints.get("suffix", ""),
        )

        section = Section(
            title=section_spec.title,
            text=text,
        )

        return section
