import os

def get_llm():
    provider = os.getenv("LLM_PROVIDER", "openai")

    if provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model="gpt-4o-mini", temperature=0)

    elif provider == "ollama":
        from langchain_community.llms import Ollama
        return Ollama(model="mistral")

    else:
        raise ValueError(f"Unsupported LLM_PROVIDER: {provider}")

