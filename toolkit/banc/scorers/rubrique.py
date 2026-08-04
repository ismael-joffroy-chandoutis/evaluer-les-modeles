"""Notation par grille a ancrages concrets, jugee par un jury multi familles.

Ce que ce scorer fait et que `model_graded_qa` ne fait pas :
  1. echelle ordinale a 4 niveaux (0 a 3) au lieu de correct / partiel / faux ;
  2. le jury est compose par candidat (exclusion de la famille jugee) ;
  3. le desaccord entre juges est CONSERVE dans la metadonnee, pas moyenne.
"""

from __future__ import annotations

import asyncio
import re
import statistics
from pathlib import Path

from inspect_ai.model import get_model
from inspect_ai.scorer import Score, Scorer, Target, mean, scorer, stderr
from inspect_ai.solver import TaskState

RACINE_RUBRIQUES = Path(__file__).resolve().parents[2] / "rubriques"

GABARIT = """Tu notes la reponse d'un modele a une epreuve d'atelier.
Tu ne reecris pas la reponse, tu ne la commentes pas pour l'ameliorer : tu la notes.

EPREUVE SOUMISE AU MODELE
{question}

CE QU'ON ATTEND (critere de l'epreuve)
{critere}

GRILLE A ANCRAGES (0 a 3)
{rubrique}

REPONSE A NOTER
{reponse}

Procede ainsi : deux phrases de justification citant un element precis de la
reponse, puis la note sur la derniere ligne, exactement au format
NOTE: <0, 1, 2 ou 3>
"""

MOTIF_NOTE = re.compile(r"NOTE\s*:\s*([0-3])", re.IGNORECASE)


def charge_rubrique(nom: str) -> str:
    chemin = RACINE_RUBRIQUES / f"{nom}.md"
    if not chemin.exists():
        raise FileNotFoundError(f"rubrique introuvable : {chemin}")
    return chemin.read_text(encoding="utf-8")


async def note_un_juge(juge: str, invite: str) -> tuple[str, int | None, str]:
    sortie = await get_model(juge).generate(invite)
    texte = sortie.completion or ""
    trouve = MOTIF_NOTE.findall(texte)
    note = int(trouve[-1]) if trouve else None
    return juge, note, texte.strip()[-400:]


async def vote_jury(juges: list[str], invite: str) -> tuple[float | None, dict]:
    """Interroge les juges en parallele, rend le vote majoritaire et la dispersion."""
    resultats = await asyncio.gather(
        *[note_un_juge(j, invite) for j in juges], return_exceptions=True
    )
    notes: dict[str, int] = {}
    incidents: dict[str, str] = {}
    justifications: dict[str, str] = {}
    for r in resultats:
        if isinstance(r, BaseException):
            incidents["exception"] = str(r)[:200]
            continue
        juge, note, extrait = r
        if note is None:
            incidents[juge] = "note illisible"
        else:
            notes[juge] = note
            justifications[juge] = extrait
    if not notes:
        return None, {"notes_par_juge": {}, "incidents": incidents}

    valeurs = list(notes.values())
    # vote majoritaire ; en cas d'egalite parfaite on prend la mediane basse,
    # qui est la lecture la moins complaisante.
    try:
        retenue = statistics.mode(valeurs)
    except statistics.StatisticsError:
        retenue = statistics.median_low(valeurs)
    meta = {
        "notes_par_juge": notes,
        "dispersion": (max(valeurs) - min(valeurs)) if len(valeurs) > 1 else 0,
        "ecart_type": statistics.pstdev(valeurs) if len(valeurs) > 1 else 0.0,
        "unanime": len(set(valeurs)) == 1,
        "justifications": justifications,
        "incidents": incidents,
    }
    return float(retenue), meta


@scorer(metrics=[mean(), stderr()])
def jury_rubrique(juges: list[str], rubrique_par_defaut: str | None = None) -> Scorer:
    """Note 0-3 (rendue sur 0-1) par vote majoritaire d'un jury multi familles.

    La rubrique utilisee est celle nommee dans `metadata["rubrique"]` de l'item,
    ce qui permet d'avoir plusieurs epreuves differentes dans une meme tache.
    """

    async def score(state: TaskState, target: Target) -> Score:
        nom_rubrique = state.metadata.get("rubrique") or rubrique_par_defaut
        invite = GABARIT.format(
            question=state.input_text,
            critere=target.text or state.metadata.get("critere", ""),
            rubrique=charge_rubrique(nom_rubrique),
            reponse=state.output.completion,
        )
        retenue, meta = await vote_jury(juges, invite)
        if retenue is None:
            return Score(value=float("nan"), explanation="aucun juge exploitable", metadata=meta)
        meta["note_brute_sur_3"] = retenue
        meta["rubrique"] = nom_rubrique
        return Score(
            value=retenue / 3.0,
            answer=state.output.completion[:400],
            explanation=f"vote majoritaire {retenue}/3 sur {len(meta['notes_par_juge'])} juges",
            metadata=meta,
        )

    return score
