from fsspec import AbstractFileSystem, get_filesystem_class
from pydantic import BaseSettings, DirectoryPath, Field, PyObject


class Settings(BaseSettings):
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    debug: str = Field(default=False)
    openai_api_key: str = Field(default="--none--")
    max_tokens: int = Field(
        default=2048, description="Max number of tokens to use in the model."
    )
    default_llm_factory: PyObject = Field(
        default="docchain.models.gpt.llm_factory",
        description="Default LLM to use for generation.",
    )
    fs_backend: str = Field(
        default="file",
        description="Filesystem backend to use. As supported by fsspec.",
    )
    fs_params: dict = Field(default={}, description="Parameters for fs_backend.")
    fs_workspace: DirectoryPath = Field(
        default=".docchain", description="All files will be stored in this directory."
    )


class LazySettings:
    """
    Instantiates settings class when first attempt to read an attribute is made.
    """

    @property
    def fs(self) -> AbstractFileSystem:
        return get_filesystem_class(self.fs_backend)(**self.fs_params)

    def __init__(self, settings_class):
        self.settings_class = settings_class
        self._instance = None

    def __getattr__(self, name):
        if self._instance is None:
            self._instance = self.settings_class()

        return getattr(self._instance, name)


conf = LazySettings(Settings)
