import json
import os
from .state import State

JOURNEY_PATH = os.path.join(os.path.dirname(__file__), '../../data/hotmart_journey.json')

# Helper to generate a deterministic mock faturamento based on user_id
FAKE_LEVELS = [
    0, 10000, 100000, 250000, 500000, 1000000, 5000000, 10000000, 25000000, 100000000, 250000000
]

def get_mock_faturamento(user_id: str) -> int:
    # Simple hash to pick a level
    idx = sum(ord(c) for c in user_id) % len(FAKE_LEVELS)
    return FAKE_LEVELS[idx]

def journey(state: State) -> dict:
    user_id = state.get('user_id', 'default')
    faturamento = get_mock_faturamento(user_id)

    with open(JOURNEY_PATH, encoding='utf-8') as f:
        journey_data = json.load(f)

    chapters = journey_data['trilhas']['legacy']['capitulos']
    found = None
    for _, chapter in chapters.items():
        for milestone in chapter['marcos']:
            # Remove non-numeric chars for comparison
            milestone_value = milestone['faturamento']
            if 'Cadastro' in milestone_value:
                value = 0
            else:
                value = int(''.join(filter(str.isdigit, milestone_value)))
            if faturamento >= value:
                found = {
                    'chapter': chapter['nome'],
                    'project': milestone['nome'],
                    'recompensas': milestone['recompensas'],
                    'faturamento': f'R$ {faturamento:,}'.replace(',', '.')
                }
            else:
                break
    if not found:
        found = {'chapter': None, 'project': None, 'recompensas': [], 'faturamento': f'R$ {faturamento:,}'.replace(',', '.')}

    message = (
        f"Você está atualmente no capítulo '{found['chapter']}' do programa, "
        f"no projeto '{found['project']}'.\n"
        f"Suas recompensas conquistadas até agora: {', '.join(found['recompensas']) if found['recompensas'] else 'nenhuma'}.\n"
        f"Seu faturamento total é de {found['faturamento']}."
    )
    
    return {"current_message": message, "user_id": state["user_id"], "messages": state.get("messages", []) + [message]}
