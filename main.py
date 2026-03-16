import sys
import typing

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

# Ensure env vars are loaded BEFORE agents SDK so the OpenAI client routes to Groq
import config

import asyncio
from agents import Runner
from agents.exceptions import InputGuardrailTripwireTriggered
from manager import manager_reviewer

BANNER = """
╔══════════════════════════════════════════════════════╗
║           AI Code Reviewer Multi-Agents              ║
║   Logique · Sécurité · Performance · Style · Doc     ║
╚══════════════════════════════════════════════════════╝
Tapez votre demande en français (ou 'quit' pour quitter)

Exemples :
  > Peux-tu analyser le fichier src/bad_code.py ?
  > Vérifie la sécurité de auth.py
"""

async def chat(query: str) -> str:
    try:
        # max_turns=20 enables full multi-agent dialogue (delegation back and forth)
        result = await Runner.run(manager_reviewer, input=query, max_turns=20)
        return result.final_output
    except InputGuardrailTripwireTriggered:
        return "Demande rejetée par les filtres."
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Erreur inattendue : {type(e).__name__}: {e}"

def main():
    print(BANNER)
    while True:
        try:
            query = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAu revoir !")
            break

        if not query:
            continue
        if query.lower() in ("quit", "exit", "q"):
            print("Au revoir !")
            break

        print("\nRecherche et Analyse en cours...\n")
        response = asyncio.run(chat(query))
        print(response)

if __name__ == "__main__":
    main()
