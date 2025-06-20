"""
Módulo responsável por realizar consultas RAG (Retrieval-Augmented Generation) usando um modelo de linguagem
e uma base de conhecimento Milvus para responder perguntas frequentes (FAQ) dos usuários Hotmart.
"""

from langchain.chat_models import ChatHuggingFace  # Modelo de chat HuggingFace (usado se não houver chave OpenAI)
from langchain.llms import HuggingFaceEndpoint     # Endpoint para modelos HuggingFace
from langchain_openai import ChatOpenAI            # Modelo de chat OpenAI

from langchain.chains import RetrievalQA           # Cadeia de perguntas e respostas com recuperação
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)

from .state import State                           # Tipo de estado compartilhado entre os nós do agente
from core.milvus.milvus_client import MilvusClient # Cliente para acesso ao banco vetorial Milvus

import os
from dotenv import load_dotenv
from pathlib import Path

# Carrega variáveis de ambiente do arquivo .env
SOURCE_PATH = os.getenv("DOTENV_PATH")
_ = load_dotenv(dotenv_path=SOURCE_PATH)

# Instruções rígidas para o modelo de linguagem, garantindo respostas baseadas apenas no contexto fornecido
SYSTEM_INSTRUCTIONS = (
    "Você é um assistente da Hotmart. "
    "Responda APENAS com base no contexto fornecido. "
    "Se não souber, diga que não sabe. "
    "Use um tom amigável, conciso e útil."
)

# Seleciona o modelo de linguagem a ser utilizado (OpenAI ou HuggingFace)
if os.getenv("OPENAI_API_KEY") is not None:
    # Usa modelo OpenAI se a chave estiver disponível
    llm = ChatOpenAI(
        model_name="gpt-4o",
        api_key=os.getenv("OPENAI_API_KEY")
    )
else:
    # Caso contrário, utiliza modelo HuggingFace hospedado
    llm_endpoint = HuggingFaceEndpoint(
        repo_id=os.getenv("HF_MODEL"),
        huggingfacehub_api_token=os.getenv("HF_TOKEN")
    )
    llm = ChatHuggingFace(llm=llm_endpoint)

# Instancia o cliente Milvus para busca vetorial
milvus = MilvusClient()

# Template de prompt para o modelo, incluindo instruções de sistema e formatação da pergunta/contexto
prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(SYSTEM_INSTRUCTIONS),
    HumanMessagePromptTemplate.from_template(
        "Contexto:\n{context}\n\nPergunta do usuário:\n{question}"
    )
])

# Cadeia de perguntas e respostas (QA) usando Milvus como base de conhecimento (RAG)
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=milvus.client.as_retriever(search_type="similarity", search_kwargs={"k": 5}),
    chain_type="stuff",
    chain_type_kwargs={"prompt": prompt}
)

def rag_query(state: State) -> dict:
    """
    Função responsável por processar uma consulta de FAQ usando RAG.
    Recebe o estado atual da conversa, executa a busca na base Milvus e retorna a resposta do modelo.

    Args:
        state (State): Estado atual da conversa, contendo a mensagem do usuário, histórico e identificador.

    Returns:
        dict: Novo estado atualizado, incluindo a resposta gerada e o histórico de mensagens.
    """
    # Extrai a pergunta do estado atual
    question = state.get("current_message", "default")
    # Executa a cadeia de QA, buscando resposta baseada no contexto recuperado
    result = qa_chain.invoke({"query": question})
    answer = result["result"]
    # Retorna o novo estado, adicionando a resposta ao histórico de mensagens
    return {
        "current_message": answer,
        "user_id": state["user_id"],
        "messages": state["messages"] + [answer]
    }