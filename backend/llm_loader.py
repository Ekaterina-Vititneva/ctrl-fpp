from langchain_community.llms import Ollama

def get_local_llm():
    return Ollama(model="mistral")
