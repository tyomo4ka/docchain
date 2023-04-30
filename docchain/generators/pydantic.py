import json

from collections.abc import Iterable

import yaml
from langchain.chains import LLMChain

from .base import BaseDocumentGenerator
from ..documents import Document, Section, PydanticFormat
from ..output_parsers.json_schema import JSONSchemaOutputParser
from ..settings import conf
from langchain.llms import BaseLLM
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser


from ..specs import (
    PydanticDocumentSpec,
    PydanticSectionSpec,
    ModelSectionSpec,
    JSONSchemaSectionSpec,
)
from ..utils import set_nested_key


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
            section = self.gen_section(section_spec)
            doc.sections.append(section)
            set_nested_key(doc_dict, section_spec.key, json.loads(section.text))

        match spec.format:
            case PydanticFormat.json:
                doc.text = json.dumps(doc_dict, indent=4)
            case PydanticFormat.yaml:
                doc.text = yaml.dump(doc_dict, indent=4)

        return doc

    def gen_section(self, spec: PydanticSectionSpec) -> Section:
        section = Section(
            title=spec.title,
        )

        match spec:
            case ModelSectionSpec():
                section.text = self.generate_model_section(spec)
            case JSONSchemaSectionSpec():
                section.text = self.generate_json_schema_section(spec)

        return section

    def generate_model_section(self, spec: ModelSectionSpec) -> str:
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

        return result

    def generate_json_schema_section(self, spec: JSONSchemaSectionSpec) -> str:
        parser = JSONSchemaOutputParser()
        default_prompt = PromptTemplate(
            template="""Give me JSON Schema for {section_name}.
{description}
{format_instructions}
        """,
            output_parser=parser,
            input_variables=["section_name", "description"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        llm_chain = LLMChain(prompt=default_prompt, llm=self.llm)
        result = llm_chain.run(
            section_name=spec.title,
            description=spec.description,
        )

        return result
