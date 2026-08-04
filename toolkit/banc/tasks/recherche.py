"""Tache recherche et lecture du banc d'essai d'atelier."""

import sys
from pathlib import Path

# Inspect charge ce fichier comme un module isole : on remet la racine du
# projet sur le chemin d'import pour que le paquet `banc` reste importable.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from inspect_ai import Task, task  # noqa: E402
from inspect_ai.solver import generate, system_message  # noqa: E402

from banc.tasks.commun import aiguilleur, charge_items, juges_pour_le_run  # noqa: E402

CONSIGNE = (
    "Tu travailles avec un cineaste qui fabrique lui-meme ses outils. "
    "Reponds en francais. Pas de tirets longs. Va au fait."
)


@task
def recherche(candidat: str | None = None, juges: str | None = None) -> Task:
    """Recherche et lecture : fidelite au corpus et claims d'absence.

    Parametres de tache :
      candidat : identifiant du modele evalue, sert a exclure sa famille du jury
      juges    : liste explicite de juges, separee par des virgules (prioritaire)
    """
    return Task(
        dataset=charge_items("recherche"),
        solver=[system_message(CONSIGNE), generate()],
        scorer=aiguilleur(juges_pour_le_run(candidat, juges)),
    )
