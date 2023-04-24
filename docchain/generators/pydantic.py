import json

from collections.abc import Iterable

import yaml
from langchain.chains import LLMChain

from .base import BaseDocumentGenerator
from ..documents import Document, Section, PydanticFormat
from docchain.settings import conf
from langchain.llms import BaseLLM
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser

from ..specs import PydanticDocumentSpec, PydanticSectionSpec


class PydanticGenerator(BaseDocumentGenerator):
    """
    Generates a document from a Pydantic model.
    """

    def __init__(self, steps: Iterable[callable] = None, llm: BaseLLM = None):
        if steps is None:
            steps = []
        super().__init__(steps)
        self.llm = llm or conf.default_llm_factory()

    def build_document(self, spec: PydanticDocumentSpec) -> Document:
        doc = Document(
            title=spec.document_title,
            filename=spec.filename,
            format=spec.format,
            text="{}",
        )

        doc_dict = {}
        for section_spec in spec.sections:
            section = self.build_section(section_spec)
            doc.sections.append(section)
            doc_dict[section_spec.key] = json.loads(section.text)

        match spec.format:
            case PydanticFormat.json:
                doc.text = json.dumps(doc_dict, indent=4)
            case PydanticFormat.yaml:
                doc.text = yaml.dump(doc_dict, indent=4)

        return doc

    def build_section(self, spec: PydanticSectionSpec) -> Section:
        section = Section(
            title=spec.title,
        )

        parser = PydanticOutputParser(pydantic_object=spec.document_schema)
        default_prompt = PromptTemplate(
            template="""
        Write {section_name} section of configuration file for {description}.

        {format_instructions}
        """,
            input_variables=["section_name", "description"],
            output_parser=parser,
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        llm_chain = LLMChain(prompt=default_prompt, llm=self.llm)
        result = llm_chain.run(
            section_name=spec.title,
            description=spec.description,
        )
        section.text = result

        return section
