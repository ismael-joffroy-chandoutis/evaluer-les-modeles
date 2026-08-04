"""Briques communes aux trois taches."""

from __future__ import annotations

import json
from pathlib import Path

from inspect_ai.dataset import MemoryDataset, Sample
from inspect_ai.scorer import Score, Scorer, Target, mean, scorer, stderr
from inspect_ai.solver import TaskState

from banc.jury import jury_pour
from banc.scorers.ecart import ecart_propositions
from banc.scorers.refus import refus_argumente
from banc.scorers.rubrique import jury_rubrique

RACINE = Path(__file__).resolve().parents[2]
ITEMS = RACINE / "items"


def charge_items(nom: str) -> MemoryDataset:
    """Charge un JSONL d'items. Remplacer le fichier suffit a changer le jeu."""
    chemin = ITEMS / f"{nom}.jsonl"
    echantillons = []
    for ligne in chemin.read_text(encoding="utf-8").splitlines():
        if not ligne.strip():
            continue
        it = json.loads(ligne)
        echantillons.append(
            Sample(
                id=it["id"],
                input=it["input"],
                target=it["critere"],
                metadata={
                    "type": it.get("type", "rubrique"),
                    "epreuve": it.get("epreuve", ""),
                    "rubrique": it.get("rubrique"),
                    "direction_valable": it.get("direction_valable", False),
                },
            )
        )
    return MemoryDataset(samples=echantillons, name=nom)


@scorer(metrics=[mean(), stderr()])
def aiguilleur(juges: list[str]) -> Scorer:
    """Un seul scorer par tache, qui route chaque item vers son epreuve.

    Inspect associe un scorer a une tache, pas a un item. Les epreuves d'une
    meme categorie n'ayant pas la meme mecanique (refus, ecart, grille), cet
    aiguilleur lit `metadata["type"]` et delegue.
    """
    par_type = {
        "refus": refus_argumente(juges),
        "ecart": ecart_propositions(juges),
        "rubrique": jury_rubrique(juges),
    }

    async def score(state: TaskState, target: Target) -> Score:
        t = state.metadata.get("type", "rubrique")
        if t not in par_type:
            raise ValueError(f"type d'epreuve inconnu : {t}")
        s = await par_type[t](state, target)
        s.metadata = {**(s.metadata or {}), "type_epreuve": t, "epreuve": state.metadata.get("epreuve")}
        return s

    return score


def juges_pour_le_run(candidat: str | None, juges_explicites: str | None) -> list[str]:
    """Compose le jury. `candidat` sert a exclure sa propre famille.

    Passer `--model` a inspect ne rend pas le nom du modele accessible au
    moment ou la tache est construite : on le repasse donc en parametre de
    tache (`-T candidat=...`), ce que `run.sh` fait automatiquement.
    """
    if juges_explicites:
        return [j.strip() for j in juges_explicites.split(",") if j.strip()]
    if not candidat:
        raise ValueError(
            "passer -T candidat=<modele> pour composer un jury hors de sa famille, "
            "ou -T juges=<liste,separee,par,virgules>"
        )
    return jury_pour(candidat)
