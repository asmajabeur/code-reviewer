# 🤖 AI Code Reviewer (Nexus Code Review)

## 📖 À propos du projet

**AI Code Reviewer** est une application web intelligente de revue de code propulsée par l'Intelligence Artificielle. Conçue avec une architecture multi-agents, elle permet d'analyser votre code sous différents angles pour en garantir sa fiabilité, sa sécurité et sa propreté. 

Plutôt que d'utiliser un seul modèle de langage générique, le système délègue la tâche à plusieurs **agents experts** qui travaillent ensemble, avant qu'un **agent orchestrateur** ne synthétise leurs diagnostics en un seul rapport Markdown clair et structuré.

## 🚀 Application Hébergée

L'application est accessible publiquement en ligne via le lien suivant :
[https://code-reviewer-agent.streamlit.app/](https://code-reviewer-agent.streamlit.app/)

## 🧠 Architecture Multi-Agents

Le système de revue de code repose sur les agents spécialisés suivants :
* **Expert Logique** : Détecte les bugs, les algorithmes sous-optimaux et les incohérences logiques dans le flux d'exécution.
* **Expert Sécurité** : Analyse le code pour identifier d'éventuelles vulnérabilités ou failles de sécurité, en proposant des corrections adaptées.
* **Expert Style** : Vérifie le respect des conventions de code, le formatage et les bonnes pratiques (Clean Code).
* **Manager (Orchestrateur)** : Compile l'ensemble des retours des experts pour générer le rapport final, en prenant soin de conserver et de mettre en évidence les blocs de code "Avant/Après".

## 🛠️ Technologies Utilisées

* **Backend** : Python avec le framework **FastAPI** garantissant une grande réactivité.
* **Frontend** : Interface utilisateur réactive et moderne (Vanilla HTML/CSS/JS) servie directement par l'API.
* **IA & LLMs** : Interface `AsyncOpenAI` avec prise en charge des API ultra-rapides de **Groq** (ex: Llama 3) et **OpenAI**.
* **Déploiement** : Prise en charge native de **Docker** pour les déploiements cloud.

## ⚙️ Installation et exécution en local

1. **Environnement Virtuel** :
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Linux/Mac
   venv\Scripts\activate     # Sur Windows
   ```

2. **Installation des dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

3. **Variables d'environnement** :
   Créez un fichier `.env` à la racine et renseignez vos clés d'API au choix :
   ```env
   GROQ_API_KEY=votre_cle_groq
   # OPENAI_API_KEY=votre_cle_openai
   ```

4. **Lancement de l'API FastAPI** :
   ```bash
   uvicorn api:app --reload
   ```

5. **Accès** : Ouvrez votre navigateur internet à l'adresse locale `http://localhost:8000/`.

## 📦 Déploiement Cloud

Pour mettre l'application en production (par exemple sur Hugging Face Spaces ou Render), consultez d'abord le fichier [`DEPLOY.md`](DEPLOY.md) qui contient l'ensemble des instructions. Un `Dockerfile` est déjà préconfiguré pour simplifier l'hébergement.
