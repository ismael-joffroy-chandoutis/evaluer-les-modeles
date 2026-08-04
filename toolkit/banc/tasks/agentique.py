"""Tache agentique : budget d'erreur.

L'affirmation a tester est celle-ci : deux modeles peuvent afficher le meme
taux de reussite alors que l'un produit beaucoup plus d'erreurs, parce que le
harnais lui laisse assez de tours pour se rattraper. En resserrant le budget
d'erreur, l'ecart reapparait.

Le dispositif est volontairement local : un outil qui valide strictement un
EDL et renvoie des erreurs precises. Pas de conteneur, pas de reseau, donc
resultat reproductible et sans dependance a Docker.

Lancer serre puis desserre :

  inspect eval banc/tasks/agentique.py --model M -T candidat=M --message-limit 6
  inspect eval banc/tasks/agentique.py --model M -T candidat=M --message-limit 24

La note ne bouge pas entre les deux si le modele est propre du premier coup.
Elle s'effondre en budget serre s'il compte sur le rattrapage.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from inspect_ai import Task, task  # noqa: E402
from inspect_ai.dataset import MemoryDataset, Sample  # noqa: E402
from inspect_ai.scorer import Score, Scorer, Target, mean, scorer, stderr  # noqa: E402
from inspect_ai.solver import TaskState, generate, system_message, use_tools  # noqa: E402
from inspect_ai.tool import ToolError, tool  # noqa: E402

PLANS = [
    ("A001C003", "01:00:12:00", "01:00:15:10"),
    ("A001C007", "02:14:03:15", "02:14:09:00"),
    ("B002C001", "10:59:58:00", "11:00:04:12"),
]

LIGNE = re.compile(
    r"^(\d{3})\s+(\S+)\s+V\s+C\s+"
    r"(\d{2}:\d{2}:\d{2}:\d{2})\s+(\d{2}:\d{2}:\d{2}:\d{2})\s+"
    r"(\d{2}:\d{2}:\d{2}:\d{2})\s+(\d{2}:\d{2}:\d{2}:\d{2})\s*$"
)


def _images(tc: str) -> int:
    h, m, s, f = (int(x) for x in tc.split(":"))
    return ((h * 60 + m) * 60 + s) * 25 + f


def valide(contenu: str) -> list[str]:
    """Rend la liste des erreurs. Liste vide = EDL accepte."""
    erreurs: list[str] = []
    lignes = [l.strip() for l in contenu.strip().splitlines() if l.strip()]
    if not lignes or not lignes[0].upper().startswith("TITLE:"):
        erreurs.append("ligne 1 : un en-tete 'TITLE:' est obligatoire")
        return erreurs
    if len(lignes) < 2 or lignes[1].upper().replace(" ", "") != "FCM:NON-DROPFRAME":
        erreurs.append("ligne 2 : 'FCM: NON-DROP FRAME' est obligatoire")
        return erreurs

    evenements = lignes[2:]
    if len(evenements) != len(PLANS):
        erreurs.append(f"{len(evenements)} evenements pour {len(PLANS)} plans attendus")
        return erreurs

    curseur = 0
    for i, (ligne, (nom, src_in, src_out)) in enumerate(zip(evenements, PLANS), start=1):
        m = LIGNE.match(ligne)
        if not m:
            erreurs.append(
                f"evenement {i} : format invalide. Attendu "
                f"'NNN NOM V C SRC_IN SRC_OUT REC_IN REC_OUT' avec NNN sur 3 chiffres"
            )
            continue
        num, source, si, so, ri, ro = m.groups()
        if int(num) != i:
            erreurs.append(f"evenement {i} : numero '{num}' au lieu de '{i:03d}'")
        if source != nom:
            erreurs.append(f"evenement {i} : source '{source}' au lieu de '{nom}'")
        if si != src_in or so != src_out:
            erreurs.append(f"evenement {i} : timecodes source attendus {src_in} et {src_out}")
        duree = _images(so) - _images(si)
        if _images(ri) != curseur:
            erreurs.append(f"evenement {i} : rec in doit continuer la timeline sans trou")
        if _images(ro) - _images(ri) != duree:
            erreurs.append(f"evenement {i} : la duree rec ne correspond pas a la duree source")
        curseur += duree
    return erreurs


@tool
def deposer_edl():
    async def executer(contenu: str) -> str:
        """Depose un EDL et le fait valider par le systeme de montage.

        Args:
            contenu: le texte complet du fichier EDL.

        Returns:
            Un message de validation, ou la liste des erreurs a corriger.
        """
        erreurs = valide(contenu)
        if erreurs:
            raise ToolError("EDL refuse :\n- " + "\n- ".join(erreurs))
        return "EDL accepte."

    return executer


CONSIGNE = (
    "Tu produis un fichier EDL au format CMX3600 pour un montage a 25 images "
    "par seconde. Tu deposes ton fichier avec l'outil `deposer_edl`. "
    "L'outil te repond ce qui ne va pas. Reponds en francais."
)

ENONCE = """Fabrique l'EDL de la sequence suivante, dans cet ordre, a 25 images par seconde.

| source   | timecode source in | timecode source out |
|----------|--------------------|---------------------|
| A001C003 | 01:00:12:00        | 01:00:15:10         |
| A001C007 | 02:14:03:15        | 02:14:09:00         |
| B002C001 | 10:59:58:00        | 11:00:04:12         |

Le montage commence a 00:00:00:00 sur la timeline et les plans s'enchainent
sans trou ni recouvrement. Titre du projet : BANC_ATELIER.
Depose le fichier avec l'outil, et corrige jusqu'a acceptation.
"""


@scorer(metrics=[mean(), stderr()])
def edl_accepte() -> Scorer:
    async def score(state: TaskState, target: Target) -> Score:
        appels = 0
        refus = 0
        accepte = False
        for m in state.messages:
            for tc in getattr(m, "tool_calls", None) or []:
                if tc.function == "deposer_edl":
                    appels += 1
            if getattr(m, "role", "") == "tool":
                # Attention : quand l'outil leve une ToolError, le texte n'est
                # PAS dans `content` (qui reste vide) mais dans `error.message`.
                # Compter les refus sur `content` seul rend toujours zero.
                erreur = getattr(m, "error", None)
                texte = str(getattr(m, "content", "")) + " " + str(
                    getattr(erreur, "message", "") if erreur else ""
                )
                if "EDL accepte" in texte:
                    accepte = True
                elif "EDL refuse" in texte:
                    refus += 1
        return Score(
            value=1.0 if accepte else 0.0,
            explanation=f"{appels} depots, {refus} refus, {'accepte' if accepte else 'echec'}",
            metadata={"depots": appels, "refus": refus, "accepte": accepte},
        )

    return score


@task
def agentique(candidat: str | None = None) -> Task:
    """Un seul item, deux budgets d'erreur. Voir l'entete du fichier."""
    return Task(
        dataset=MemoryDataset(
            samples=[Sample(id="edl-cmx3600", input=ENONCE, target="EDL accepte")],
            name="agentique",
        ),
        solver=[system_message(CONSIGNE), use_tools(deposer_edl()), generate()],
        scorer=edl_accepte(),
    )
