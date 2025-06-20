from langgraph.graph import END, StateGraph

from chat_agents.utils.chat_node import chat
from chat_agents.utils.faq_node import rag_query
from chat_agents.utils.router_node import router
from chat_agents.utils.journey_node import journey
from chat_agents.utils.state import State

from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
import time

# Criação do grafo de estados principal para o fluxo do agente
graph_builder = StateGraph(State)

# Adiciona os nós principais do grafo, cada um responsável por uma função do agente
graph_builder.add_node("chat", chat)
graph_builder.add_node("faq", rag_query)
graph_builder.add_node("journey", journey)
graph_builder.add_node("router", router)

# Define o ponto de entrada do grafo
graph_builder.set_entry_point("chat")

# Define as transições condicionais a partir do nó de roteamento principal
graph_builder.add_conditional_edges("router", router, {
    "faq": "faq",
    "journey": "journey"
})

# Após responder FAQ ou Journey, retorna ao chat
graph_builder.add_edge("faq", END)
graph_builder.add_edge("journey", END)

# Define o ponto de finalização do grafo
#graph_builder.set_finish_point(END)

# Compila o grafo para execução
graph = graph_builder.compile()

# Instancia a aplicação FastAPI
app = FastAPI()

class Query(BaseModel):
    """
    Modelo de dados para requisições de chat.
    """
    question: str
    user_id: str = "default"

@app.post("/chat")
def chat_with_agent(query: Query):
    """
    Endpoint principal para interação com o agente conversacional.
    Recebe uma pergunta e retorna a resposta do agente, mantendo o histórico de mensagens.
    
    Args:
        query (Query): Dados da requisição contendo a pergunta, user_id, timestamp e histórico.
    
    Returns:
        dict: Resposta do agente e estado atualizado.
    """

    result = graph.invoke({
        "query": query.question,
        "user_id": query.user_id,
    })

    return result