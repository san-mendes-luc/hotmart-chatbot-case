from .state import State


def router(state: State) -> str:
    # Simple keyword-based decision logic
    print(state.keys)

    query = state.get("current_message", "").lower()

    keywords = ["meu status", "minha jornada", "meu nível", "hotmart journey", "estou em que nível", "estou no legacy", "estou no stars"]
    
    if any(keyword in query for keyword in keywords):
        return "journey"
    
    return "faq"