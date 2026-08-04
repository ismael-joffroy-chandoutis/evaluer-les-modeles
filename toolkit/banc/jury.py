"""Jury multi familles.

Regle du protocole : jamais un juge de la meme famille que le modele juge.

Inspect AI accepte nativement une liste de modeles juges dans `model_graded_qa`
et reduit par vote majoritaire (`multi_scorer(scorers, "mode")`). Mais cette
liste est FIXE pour toute la tache : elle ne sait pas exclure la famille du
modele evalue. C'est ce module qui fait ce travail, en composant un jury
different pour chaque candidat.
"""

from __future__ import annotations

# Un juge par famille. Modeles peu chers mais competents : un juge coute
# autant d'appels que d'items, multiplie par le nombre de candidats.
POOL_JUGES: dict[str, str] = {
    "openai": "openrouter/openai/gpt-5.4-mini",
    "google": "openrouter/google/gemini-3.5-flash",
    "anthropic": "openrouter/anthropic/claude-sonnet-5",
    "qwen": "openrouter/qwen/qwen3.7-plus",
    "deepseek": "openrouter/deepseek/deepseek-v4-pro",
    "xai": "openrouter/x-ai/grok-4.3",
}

# Alias de familles tels qu'ils apparaissent dans les identifiants OpenRouter.
_ALIAS = {
    "x-ai": "xai",
    "mistralai": "mistral",
    "meta-llama": "meta",
}


def famille(modele: str) -> str:
    """Extrait la famille d'un identifiant de modele.

    >>> famille("openrouter/anthropic/claude-sonnet-5")
    'anthropic'
    >>> famille("openrouter/x-ai/grok-4.3")
    'xai'
    """
    parties = [p for p in modele.split("/") if p]
    if len(parties) >= 3:
        brut = parties[1]
    elif len(parties) == 2:
        brut = parties[0]
    else:
        brut = parties[0]
    return _ALIAS.get(brut, brut)


def jury_pour(candidat: str, taille: int = 3, pool: dict[str, str] | None = None) -> list[str]:
    """Compose un jury de `taille` juges, aucun de la famille du candidat.

    Leve une erreur si le pool ne contient pas assez de familles distinctes :
    mieux vaut refuser de tourner que de produire un score contamine par
    l'auto-preference.
    """
    pool = pool or POOL_JUGES
    exclue = famille(candidat)
    juges = [m for f, m in pool.items() if f != exclue]
    if len(juges) < taille:
        raise ValueError(
            f"pool insuffisant : {len(juges)} juges hors famille '{exclue}', "
            f"{taille} demandes"
        )
    return juges[:taille]
