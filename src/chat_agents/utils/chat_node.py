from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage
from langchain.chat_models import ChatHuggingFace
from langchain.llms import HuggingFaceEndpoint
from langchain_openai import ChatOpenAI


from .state import State

import os
from dotenv import load_dotenv
from pathlib import Path

SOURCE_PATH = os.getenv("DOTENV_PATH")
_ = load_dotenv(dotenv_path=SOURCE_PATH)

if os.getenv("OPENAI_API_KEY"):
    llm = ChatOpenAI(
        model_name="gpt-4o",
        api_key=os.getenv("OPENAI_API_KEY")
    )
else:
    llm_endpoint = HuggingFaceEndpoint(
        repo_id=os.getenv("HF_MODEL"),
        huggingfacehub_api_token=os.getenv("HF_TOKEN")
    )

    llm = ChatHuggingFace(llm=llm_endpoint)


def chat(state: State) -> dict:

    messages = (
        "Você é o assistente da Hotmart."
        "A sua principal função é ajudar os usuários da Hotmart em suas dúvidas."
        "Use um tom amigável e acolhedor. Mensagens concisas, objetivas e claras ajudam o usuário a chegar no sucesso na resolução do seu problema."
        f"Usuário: {state.get('query')}"
    )

    message = llm.invoke(messages)  # Generate response
    return {"messages": [message]}  # Return updated messages