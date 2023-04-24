from langchain.chat_models import ChatOpenAI


def llm_factory():
    return ChatOpenAI(model_name="gpt-3.5-turbo-0301", temperature=0.5, max_tokens=2048)
