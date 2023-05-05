import json
from logging import getLogger

from langchain.callbacks import get_openai_callback

from docchain.specs import Spec

from ..settings import conf

logger = getLogger(__name__)


def collect_openai_stats(build_document):
    def run(spec: Spec):
        with get_openai_callback() as cb:
            document = build_document(spec)

        if document.filename and conf.debug:
            with conf.fs.open(
                f"{conf.fs_workspace}/{document.filename}.stats", "w+"
            ) as file:
                stats = {
                    "total_tokens": cb.total_tokens,
                    "prompt_tokens": cb.prompt_tokens,
                    "completion_tokens": cb.completion_tokens,
                    "successful_requests": cb.successful_requests,
                    "total_cost": cb.total_cost,
                }
                file.write(json.dumps(stats))

        document.stats = stats

        return document

    return run
