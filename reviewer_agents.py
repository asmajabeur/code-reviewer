from agents import Agent, Runner, function_tool
from config import groq_model
from tools import read_code, search_cve

# ── 1. AGENTS SPÉCIALISÉS ──

agent_logic = Agent(
    name="Agent_Logique",
     instruções=(
        "Tu es l'EXPERT EN FIABILITÉ de l'agent de Code Review. Ton rôle est de garantir "
        "que le code est fonctionnel, respecte les standards de l'industrie et reste facile "
        "à maintenir en éliminant la redondance.\n\n"
        "1. Détection de Bugs & Erreurs Courantes (logique métier, variables non initialisées, edge cases).\n"
        "2. Conformité aux Conventions de Style (PEP 8, nommage, formatage).\n"
        "3. Identification de Code Dupliqué & Redondant.\n\n"
        "Tu dois utiliser l'outil `read_code` pour inspecter le fichier source fourni par le Manager.\n"
        "🛑 RÈGLE ABSOLUE : Pour CHAQUE problème que tu trouves, tu DOIS fournir un exemple en Markdown de code corrigé (un bloc 'Avant' / 'Après').\n"
        "Sois concis, pédagogique et formatte tes retours techniquement."
    ),
    tools=[read_code],
    model=groq_model,
)

agent_security = Agent(
    name="Agent_Securite",
    instructions=(
        "Tu es l'EXPERT EN PROTECTION ET OPTIMISATION de l'agent de Code Review. Ton rôle est de garantir "
        "que le code est invulnérable aux attaques et efficace.\n\n"
        "1. Vérification de la Sécurité : Injections SQL, XSS, CSRF, secrets exposés en clair.\n"
        "2. Analyse de Performance : Complexité algorithmique O(n), boucles inefficaces, fuites.\n\n"
        "Tu dois utiliser l'outil `read_code` pour inspecter le fichier source. "
        "Tu DOIS utiliser l'outil `search_cve` pour vérifier si les librairies importées ont des "
        "vulnérabilités connues.\n"
        "🛑 RÈGLE ABSOLUE : Chaque fois que tu signales une faille ou une lenteur, tu DOIS écrire le bloc de code brut de la solution sécurisée/optimisée en Markdown.\n"
        "Priorise les failles critiques."
    ),
    tools=[read_code, search_cve],
    model=groq_model,
)

agent_style = Agent(
    name="Agent_Style_Doc",
    instructions=(
        "Tu es l'EXPERT EN DOCUMENTATION ET PÉDAGOGIE. "
        "Tu vérifies la qualité des commentaires, des docstrings, et tu expliques "
        "didactiquement les problèmes détectés pour faire progresser le développeur. "
        "Utilise `read_code` pour lire le fichier.\n"
        "🛑 RÈGLE ABSOLUE : Si la documentation ou le format est manquant, tu DOIS réécrire intégralement la fonction ou la classe avec la docstring propre en format Markdown."
    ),
    tools=[read_code],
    model=groq_model,
)

# ── 2. TOOLS DE DÉLÉGATION (Pattern agents-as-tools) ──

@function_tool
async def deleguer_agent_logic(filepath: str) -> str:
    """Délègue l'analyse d'un fichier source à l'Agent Logique pour chercher les bugs, redondances et problèmes de style de code.
    Args:
        filepath: Le chemin vers le fichier de code à analyser.
    """
    result = await Runner.run(agent_logic, input=f"Analyse ce fichier: {filepath}", max_turns=5)
    return result.final_output


@function_tool
async def deleguer_agent_security(filepath: str) -> str:
    """Délègue l'analyse d'un fichier source à l'Agent Sécurité pour chercher les failles (SQLi, XSS, secrets en clair) et problèmes de performances.
    Args:
        filepath: Le chemin vers le fichier de code à analyser.
    """
    result = await Runner.run(agent_security, input=f"Analyse la sécurité de ce fichier: {filepath}", max_turns=5)
    return result.final_output


@function_tool
async def deleguer_agent_style(filepath: str) -> str:
    """Délègue l'analyse d'un fichier source à l'Agent Style/Doc pour vérifier la qualité de la documentation et la pédagogie.
    Args:
        filepath: Le chemin vers le fichier de code à analyser.
    """
    result = await Runner.run(agent_style, input=f"Vérifie la documentation de ce fichier: {filepath}", max_turns=5)
    return result.final_output
