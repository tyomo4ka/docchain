from pydantic import BaseSettings, DirectoryPath, Field, PyObject


class Settings(BaseSettings):
    debug: str = Field(default=False)
    openai_api_key: str = Field(default="--none--")
    workspace: DirectoryPath = Field(
        default=".docchain", description="All files will be stored in this directory."
    )
    max_tokens: int = Field(
        default=2048, description="Max number of tokens to use in the model."
    )
    default_llm_factory: PyObject = Field(
        default="docchain.models.gpt.llm_factory",
        description="Default LLM to use for generation.",
    )


class LazySettings:
    """
    Instantiates settings class when first attempt to read an attribute is made.
    """

    def __init__(self, settings_class):
        self.settings_class = settings_class
        self._instance = None

    def __getattr__(self, name):
        if self._instance is None:
            self._instance = self.settings_class()

        return getattr(self._instance, name)


conf = LazySettings(Settings)
