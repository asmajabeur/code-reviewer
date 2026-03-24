from agents import Agent
from config import groq_model
from reviewer_agents import deleguer_agent_logic, deleguer_agent_security, deleguer_agent_style

def get_manager_reviewer():
    """
    Crée et retourne l'agent orchestrateur (Mode No-Tools).
    Puisque Groq a désactivé son modèle de fonction, l'Orchestrateur agira juste comme synthétiseur classique.
    """
    return Agent(
        name="Agent_Orchestrateur",
        instructions=(
            "Tu es le CHEF D'ORCHESTRE d'un système de Code Review Multi-Agents.\n"
            "Tu vas recevoir le texte brut contenant les analyses détaillées de 3 experts (Logique, Sécurité, Style).\n\n"
            "Ton SEUL et UNIQUE rôle est de :\n"
            "1. Lire attentivement les 3 rapports fournis dans le prompt.\n"
            "2. Les fusionner harmonieusement en un SEUL rapport final MAGNIFIQUE et STRUCTURÉ en Markdown.\n"
            "3. 🛑 RÈGLE ABSOLUE : Tu DOIS conserver TOUS LES BLOCS DE CODE (Avant/Après) donnés par les experts dans ta synthèse finale.\n"
            "4. Ne mentionne pas le processus interne, présente simplement le résultat brut stylisé et professionnel."
        ),
        model=groq_model,
    )
