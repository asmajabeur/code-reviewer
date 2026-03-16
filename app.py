import sys
import typing

# === MONKEYPATCH POUR FIXER LE BUG D'OPENAI-AGENTS AVEC PYTHON 3.11 ===
if sys.version_info[:3] == (3, 11, 0):
    def _patched_determine_new_args(self, args):
        params = self.__parameters__
        for param in params:
            prepare = getattr(param, '__typing_prepare_subst__', None)
            if prepare is not None:
                args = prepare(self, args)
        alen = len(args)
        plen = len(params)
        if alen != plen:
            raise TypeError(f"Too {'many' if alen > plen else 'few'} arguments for {self};"
                            f" actual {alen}, expected {plen}")
        new_arg_by_param = dict(zip(params, args))

        new_args = []
        for old_arg in self.__args__:
            substfunc = getattr(old_arg, '__typing_subst__', None)
            if substfunc:
                new_arg = substfunc(new_arg_by_param[old_arg])
            else:
                subparams = getattr(old_arg, '__parameters__', ())
                if not subparams:
                    new_arg = old_arg
                else:
                    subargs = []
                    for x in subparams:
                        if isinstance(x, typing.TypeVarTuple):
                            subargs.extend(new_arg_by_param.get(x, []))
                        else:
                            subargs.append(new_arg_by_param.get(x, typing.Any))
                    new_arg = old_arg[tuple(subargs)]

            if self.__origin__ == getattr(typing, 'collections', globals().get('collections', dict)).abc.Callable and isinstance(new_arg, tuple):
                new_args.extend(new_arg)
            elif getattr(typing, '_is_unpacked_typevartuple', lambda x: False)(old_arg):
                new_args.extend(new_arg)
            else:
                new_args.append(new_arg)
        return tuple(new_args)
        
    typing._GenericAlias._determine_new_args = _patched_determine_new_args

import streamlit as st
import asyncio
import os
import tempfile
import config # Charge les variables d'environnement et configure l'API Groq BEFORE agents
from manager import manager_reviewer
from agents import Runner


# ==========================================
# CONFIGURATION DE LA PAGE STREAMLIT
# ==========================================
# st.set_page_config définit l'apparence globale de l'onglet du navigateur
st.set_page_config(
    page_title="AI Code Reviewer", 
    page_icon="🤖", 
    layout="wide"
)

# ==========================================
# TITRE ET DESCRIPTION DE L'APPLICATION
# ==========================================
st.title("🛡️ Système Multi-Agents de Code Review automatisé")
st.markdown(
    """
    Bienvenue dans la **Revue de Code Augmentée par l'IA**. 
    Ce système utilise une équipe d'agents spécialisés (Logique, Sécurité, Style) 
    coordonnés par un **Orchestrateur** pour analyser votre code source en profondeur.
    
    👉 **Instructions :** Chargez un fichier de code (React, Java, Python, C#, etc.), ou tapez directement 
    votre code dans la zone de texte prévue à cet effet.
    """
)

# ==========================================
# GESTION ASYNCHRONE DE LA REVUE DE CODE
# ==========================================
async def lancer_processus_code_review(filepath_to_review: str):
    """
    Fonction asynchrone qui appelle le Runner de 'openai-agents'.
    L'orchestrateur (manager_reviewer) reçoit la directive de lire et d'analyser le fichier.
    """
    prompt_initial = f"Peux-tu analyser le fichier suivant et me faire un rapport complet : {filepath_to_review}"
    
    # Runner.run démarre la boucle multi-agents de l'Orchestrateur
    result = await Runner.run(
        manager_reviewer, 
        input=prompt_initial, 
        max_turns=30 # Limite le nombre maximum d'échanges entre les agents
    )
    return result

# ==========================================
# INTERFACE UTILISATEUR : UPLOAD OU SAISIE
# ==========================================

# Utilisation de colonnes pour séparer les options du contenu principal
col_options, col_main = st.columns([1, 2], gap="large")

with col_options:
    st.header("⚙️ Entrée du code")
    st.info("Sélectionnez la méthode pour fournir votre code source.")
    
    # Option pour le mode d'entrée du code
    input_method = st.radio(
        "Comment souhaitez-vous fournir le code ?", 
        ("Importer un fichier", "Taper du code manuellement")
    )
    
    filepath_to_analyze = None

with col_main:
    st.header("📄 Source à analyser")
    if input_method == "Importer un fichier":
        # Composant Streamlit permettant de charger un fichier
        uploaded_file = st.file_uploader("Choisissez un fichier de code", type=["py", "js", "jsx", "ts", "tsx", "java", "cs", "cpp", "c", "php", "rb", "txt", "md"])
        
        if uploaded_file is not None:
            # Si un fichier est chargé, on l'affiche pour confirmation dans un expander pour gagner de la place
            code_content = uploaded_file.getvalue().decode("utf-8")
            with st.expander("👁️ Voir le contenu du fichier", expanded=True):
                st.code(code_content)

            # Enregistrement temporaire sur le disque
            with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode='w', encoding='utf-8') as tmp_file:
                tmp_file.write(code_content)
                filepath_to_analyze = tmp_file.name
        else:
            st.warning("👈 Veuillez charger un fichier dans la colonne de gauche.")

    elif input_method == "Taper du code manuellement":
        # Composant Streamlit permettant de taper du texte libre
        code_content = st.text_area("Tapez ou collez votre code ici :", height=250, placeholder="Ex: const sayHello = () => { console.log('Hello World!'); }")
        
        if code_content.strip():
            # Si la zone de texte n'est pas vide, on crée également un fichier temporaire
            with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode='w', encoding='utf-8') as tmp_file:
                tmp_file.write(code_content)
                filepath_to_analyze = tmp_file.name
        else:
            st.warning("Tapez du code ci-dessus pour activer l'analyse.")

st.divider() # Ligne de séparation esthétique

# ==========================================
# BOUTON DE LANCEMENT DE L'ANALYSE
# ==========================================
# Le bouton "Lancer la Code Review" n'est actif que si un fichier est prêt à être analysé
if filepath_to_analyze:
    if st.button("🚀 Lancer la Code Review Multi-Agents", type="primary"):
        
        # 'st.spinner' affiche une animation circulaire pendant le traitement
        with st.spinner("L'Orchestrateur coordonne l'équipe... Veuillez patienter (cela peut prendre jusqu'à une minute)."):
            try:
                # Exécution de la fonction asynchrone (nécessaire car Streamlit est synchrone par défaut)
                resultat_review = asyncio.run(lancer_processus_code_review(filepath_to_analyze))
                
                # Succès ! Affichage du résultat final envoyé par l'agent Orchestrateur
                st.success("✅ Analyse terminée avec succès !")
                
                # Organisation du rendu visuel avec un encart esthétique pour le rapport
                st.subheader("📊 Rapport Final de la Code Review")
                st.markdown("---") # Ligne de séparation
                
                # Le contenu du rapport markdown est formaté et affiché par Streamlit
                st.markdown(resultat_review.final_output)
                
            except Exception as e:
                # Gestion des erreurs propre
                st.error(f"❌ Une erreur interne est survenue lors de l'exécution des agents : {str(e)}")
            
            finally:
                # Quoi qu'il arrive (succès ou erreur), on nettoie le disque en supprimant le fichier temporaire
                if os.path.exists(filepath_to_analyze):
                    try:
                        os.remove(filepath_to_analyze)
                    except:
                        pass
else:
    st.info("Veuillez charger un fichier ou écrire du code pour activer le bouton d'analyse.")

# ==========================================
# PIED DE PAGE EXPLICATIF (PÉDAGOGIQUE)
# ==========================================
st.markdown("---")
with st.expander("ℹ️ Comment fonctionnent ces agents en coulisses ?"):
    st.markdown(
        """
        ### L'Architecture Multi-Agents expliquée :
        Ce projet repose sur le framework **`openai-agents`** et le modèle **`llama-3.3-70b-versatile`** (fourni par **Groq** via un proxy pour court-circuiter l'attente OpenAI). 
        1. **`manager.py` (L'Orchestrateur)** : Le point d'entrée. Il ne lit jamais le code.
        2. L'Orchestrateur délègue l'analyse brute à 3 experts (`reviewer_agents.py`) :
           * 🕵️‍♂️ **L'Agent Logique** : Traque les bugs métiers et soucis d'architecture.
           * 🛡️ **L'Agent Sécurité** : Vérifie la viabilité des packages importés (Outil `search_cve` branché sur l'API publique OSV) et les failles (SQLi, secrets en dur).
           * ✍️ **L'Agent Style & Doc** : Audit de la PEP8 et de la pédagogie des commentaires.
        3. Chacun répond à l'Orchestrateur, qui synthétise tous les retours en un seul **rapport cohérent** que vous lisez ci-dessus.
        """
    )
