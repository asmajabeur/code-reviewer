# Mettre le code en production

L'outil **Code Reviewer IA v2.0** a été architecturé pour fonctionner gratuitement sur **Hugging Face Spaces** (Docker) ou **Render**.
Puisque le nouveau design HTML personnalisé gère tout le visuel de manière native, le serveur cloud n'a besoin d'exécuter que l'API Python pure (`FastAPI`). Streamlit n'est plus requis en mode déploiement, ce qui baisse la consommation RAM de 80% !

## Déploiement sur Hugging Face Spaces (Gratuit)

1. Rendez-vous sur [Hugging Face Spaces](https://huggingface.co/spaces) et créez un Space.
2. Choisissez le mode **Docker** (Blank).
3. Transférez-y tous les fichiers du dossier actuel avec l'interface GitHub intégrée.
4. Dans les paramètres (Settings > Variables and secrets) du Space, ajoutez votre **`GROQ_API_KEY`** (ou `OPENAI_API_KEY`).
5. C'est tout. Hugging Face va lire le `Dockerfile`, installer les dépendances et démarrer le serveur automatiquement sur le port 7860.

Votre application sera publique et accessible depuis n'importe quel ordinateur ou smartphone, avec un design fluide, premium et rapide !

## Remarques importantes :
*   L'URL absolue `localhost:8000` au sein du ficher `index.html` a été remplacée au profit d'une requête URL relative de production `/analyze`. Cela permet à l'interface HTML de comprendre automatiquement qu'elle doit taper sur l'API située à la racine du domaine d'hébergement.
*   Assurez-vous que les packages FastAPI (`fastapi`) et serveurs asynchrones (`uvicorn`) figurent bien au complet dans le `requirements.txt`.
