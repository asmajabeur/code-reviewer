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
            raise TypeError(f"Too {'many' if alen > plen else 'few'} arguments")
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

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import os
import tempfile
import config  # Assure le chargement de l'API Key Groq via _openai_shared
from manager import get_manager_reviewer
from agents import Runner
from reviewer_agents import deleguer_agent_logic, deleguer_agent_security, deleguer_agent_style

app = FastAPI(title="Nexus Code Review API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    code: str
    filename: str
    use_logic: bool
    use_security: bool
    use_style: bool
    depth: str  # "RAPIDE", "STANDARD", "EXHAUSTIF"

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/analyze")
async def analyze_code(req: AnalyzeRequest):
    # Enregistrer le code temporairement pour que les sous-agents puissent le lire
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode='w', encoding='utf-8') as tmp_file:
        tmp_file.write(req.code)
        filepath = tmp_file.name

    try:
        # Exécution manuelle des experts (No-Tools)
        filepath_clean = filepath.replace("\\", "/")
        rapports_bruts = []
        
        if req.use_logic:
            res_logic = await deleguer_agent_logic(req.code, req.filename)
            rapports_bruts.append(f"### RAPPORT EXPERT LOGIQUE :\n{res_logic}")
            
        if req.use_security:
            res_security = await deleguer_agent_security(req.code, req.filename)
            rapports_bruts.append(f"### RAPPORT EXPERT SÉCURITÉ :\n{res_security}")
            
        if req.use_style:
            res_style = await deleguer_agent_style(req.code, req.filename)
            rapports_bruts.append(f"### RAPPORT EXPERT STYLE :\n{res_style}")
            
        if not rapports_bruts:
            rapports_bruts.append("Aucun agent n'a été activé par l'utilisateur.")
            
        texte_fusionne = "\n\n---\n\n".join(rapports_bruts)

        # Création du manager synthétiseur
        manager_synthetiseur = get_manager_reviewer()
        
        # Mapping de profondeur
        consignes = {
            "RAPIDE": "Fais un résumé très rapide.",
            "STANDARD": "Fais une synthèse standard équilibrée.",
            "EXHAUSTIF": "Fais une compilation ultra-complète et méticuleuse."
        }
        consigne_profondeur = consignes.get(req.depth, consignes["STANDARD"])
        
        prompt_final = f"Voici les rapports bruts de tes sous-agents concernant le fichier {req.filename}. Directive de profondeur : {consigne_profondeur}\nRAPPORTS:\n\n{texte_fusionne}"
        
        # Le manager n'a plus d'outils, il lit juste le prompt et le synthétise
        result = await Runner.run(manager_synthetiseur, input=prompt_final, max_turns=5)
        
        return JSONResponse(content={"markdown_report": result.final_output})
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except:
                pass
