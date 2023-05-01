import json
import yaml
import os
from collections.abc import Iterable
from copy import deepcopy
from logging import getLogger
from langchain.chains import LLMChain
from langchain.llms import BaseLLM
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from .exceptions import DocumentGenerationError
from .output_parsers.json_schema import JSONSchemaOutputParser
from .specs import (
    Spec,
    BaseSectionSpec,
    TextSectionSpec,
    ModelSectionSpec,
    JSONSchemaSectionSpec,
)
from .documents import Document, PydanticFormat, Section
from .settings import conf
from .utils import set_nested_key

logger = getLogger(__name__)


class Generator:
    def __init__(self, steps: Iterable[callable] = None, llm: BaseLLM = None):
        self.steps = steps or []
        handler = self.build_document
        for step in self.steps:
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
                    fname = f"{conf.workspace}/failed/{spec.document_title}"
                    os.makedirs(os.path.dirname(fname), exist_ok=True)
                    with open(
                        f"{conf.workspace}/failed/{spec.document_title}", mode="a+"
                    ) as file:
                        file.write(str(spec.doc.dict()))

            raise DocumentGenerationError("Document generation failed") from exc

        return document

    def __call__(self, spec: Spec) -> Document:
        # As generator can optionally modify spec, ensure it's dealing with a copy
        spec_copy = deepcopy(spec)
        doc = self._build_document(spec_copy)

        return doc

    def build_document(self, spec: Spec) -> Document:
        doc = Document(
            title=spec.document_title,
            filename=spec.filename,
            format=spec.format,
            text="{}",
        )

        doc_dict = {}
        for section_spec in spec.sections:
            section = self.gen_section(section_spec, spec)
            doc.sections.append(section)
            set_nested_key(doc_dict, section_spec.key, json.loads(section.text))

        match spec.format:
            case PydanticFormat.json:
                doc.text = json.dumps(doc_dict, indent=4)
            case PydanticFormat.yaml:
                doc.text = yaml.dump(doc_dict, indent=4)
            case PydanticFormat.text:
                doc.text = [f"{key}\n\n{value}" for key, value in doc_dict]

        return doc

    def gen_section(self, section_spec: BaseSectionSpec, doc_spec: Spec) -> Section:
        section = Section(
            title=section_spec.title,
        )

        match section_spec:
            case ModelSectionSpec():
                section.text = self.generate_model_section(section_spec, doc_spec)
            case JSONSchemaSectionSpec():
                section.text = self.generate_json_schema_section(section_spec, doc_spec)
            case TextSectionSpec():
                section.text = self.generate_text_section(section_spec, doc_spec)

        return section

    def generate_model_section(self, spec: ModelSectionSpec, *args, **kwargs) -> str:
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

    def generate_json_schema_section(
        self, spec: JSONSchemaSectionSpec, *args, **kwargs
    ) -> str:
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

    def generate_text_section(
        self, spec: TextSectionSpec, doc_spec: Spec, *args, **kwargs
    ) -> str:
        prompt = PromptTemplate(
            template="""
        Write {section_name} section of {document_name} document.

        {description}
        """,
            input_variables=[
                "section_name",
                "document_name",
                "description",
            ],
        )
        llm_chain = LLMChain(prompt=prompt, llm=self.llm)

        result = llm_chain.run(
            section_name=spec.title,
            document_name=doc_spec.document_name,
            description=spec.description,
        )

        return result
