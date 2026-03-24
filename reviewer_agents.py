from agents import Agent, Runner
from config import groq_model
from tools import search_cve

# ── 1. AGENTS SPÉCIALISÉS ──

agent_logic = Agent(
    name="Agent_Logique",
     instructions=(
        "Tu es l'EXPERT EN FIABILITÉ. Ton rôle est de garantir que le code fourni est fonctionnel, "
        "respecte les standards de l'industrie et reste facile à maintenir.\n\n"
        "1. IDENTIFIE IMMÉDIATEMENT LE LANGAGE DE PROGRAMMATION du code analysé.\n"
        "2. Détection de Bugs & Erreurs Courantes propres à ce langage.\n"
        "3. Conformité aux Conventions de Style spécifiques du langage détecté.\n"
        "4. Identification de Code Dupliqué & Redondant.\n\n"
        "🛑 RÈGLE ABSOLUE : Pour CHAQUE problème que tu trouves, tu DOIS fournir un exemple en Markdown de code corrigé (un bloc 'Avant' / 'Après').\n"
        "Sois concis, pédagogique et formatte tes retours techniquement."
    ),
    model=groq_model,
)

agent_security = Agent(
    name="Agent_Securite",
    instructions=(
        "Tu es l'EXPERT EN PROTECTION ET OPTIMISATION. Ton rôle est de garantir que le code est invulnérable aux attaques et efficace.\n\n"
        "1. IDENTIFIE LE LANGAGE DE PROGRAMMATION du code et les écosystèmes utilisés.\n"
        "2. Vérification de la Sécurité spécifique au langage : Injections SQL, XSS, CSRF, secrets exposés en clair.\n"
        "3. Analyse de Performance : Complexité algorithmique O(n), boucles inefficaces, fuites.\n\n"
        "🛑 RÈGLE ABSOLUE : Chaque fois que tu signales une faille ou une lenteur, tu DOIS écrire le bloc de code brut de la solution sécurisée/optimisée en Markdown.\n"
        "Priorise les failles critiques."
    ),
    model=groq_model,
)

agent_style = Agent(
    name="Agent_Style_Doc",
    instructions=(
        "Tu es l'EXPERT EN DOCUMENTATION ET PÉDAGOGIE. "
        "Tu vérifies la qualité des commentaires, des docstrings, et tu expliques "
        "didactiquement les problèmes détectés pour faire progresser le développeur.\n"
        "🛑 RÈGLE ABSOLUE : Si la documentation ou le format est manquant, tu DOIS réécrire intégralement la fonction ou la classe avec la docstring propre en format Markdown."
    ),
    model=groq_model,
)

# ── 2. FONCTIONS DE DÉLÉGATION DIRECTES (No-Tools Pattern) ──

async def deleguer_agent_logic(code: str, filename: str) -> str:
    """Délègue l'analyse à l'Agent Logique via Injection Directe."""
    result = await Runner.run(agent_logic, input=f"Analyse ce code ({filename}):\n\n```\n{code}\n```", max_turns=2)
    return result.final_output


async def deleguer_agent_security(code: str, filename: str) -> str:
    """Délègue l'analyse à l'Agent Sécurité via Injection Directe."""
    result = await Runner.run(agent_security, input=f"Analyse la sécurité de ce code ({filename}):\n\n```\n{code}\n```", max_turns=2)
    return result.final_output


async def deleguer_agent_style(code: str, filename: str) -> str:
    """Délègue l'analyse à l'Agent Style via Injection Directe."""
    result = await Runner.run(agent_style, input=f"Vérifie la documentation de ce code ({filename}):\n\n```\n{code}\n```", max_turns=2)
    return result.final_output
