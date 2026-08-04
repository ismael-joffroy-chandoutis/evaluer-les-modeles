"""Scorer de l'ecart entre propositions (mesure anti homogeneisation).

On demande N directions. On ne note pas la meilleure, on note la distance entre
elles. Un modele qui rend cinq variantes de la meme idee echoue, meme si l'idee
est bonne.

Deux mesures, gardees separees puis combinees :

  - `diversite_lexicale` : deterministe, sans appel modele. 1 moins la moyenne
    des similarites de Jaccard sur les mots pleins, entre toutes les paires de
    propositions. Attrape la reformulation, pas la redondance conceptuelle.
  - `note_jury` : un jury multi familles compte combien de directions sont
    STRUCTURELLEMENT distinctes (dispositif, point de vue, materiau), pas
    seulement formulees autrement. Attrape la redondance conceptuelle.

La note finale pondere 0,6 le jury et 0,4 le lexical. Les deux composantes
restent dans la metadonnee : si elles divergent fortement, c'est le signal que
le modele varie le vocabulaire sans varier l'idee (ou l'inverse).
"""

from __future__ import annotations

import itertools
import re
import unicodedata

from inspect_ai.scorer import Score, Scorer, Target, mean, scorer, stderr
from inspect_ai.solver import TaskState

from .rubrique import charge_rubrique, vote_jury

# Mots vides francais : sans eux la similarite de Jaccard mesure surtout la
# grammaire commune a toutes les phrases.
MOTS_VIDES = set(
    """a au aux avec ce ces cet cette dans de des du elle en et eux il ils je la le les
leur lui ma mais me meme mes moi mon ne nos notre nous on ou par pas plus pour qu que
qui sa se ses son sur ta te tes toi ton tu un une vos votre vous y c d j l m n s t est
sont etre ete avoir comme si sans sous entre vers chez donc or ni car quand aussi tres
peut plutot alors deja encore toujours jamais rien tout tous toute toutes autre autres
faire fait fais dire dit direction proposition piste idee film plan scene sequence""".split()
)

MOTIF_BLOC = re.compile(r"(?m)^\s*(?:[#*_\s]*)(?:direction\s*)?(\d)[\.\)\:]", re.IGNORECASE)


def _normalise(mot: str) -> str:
    mot = unicodedata.normalize("NFD", mot.lower())
    return "".join(c for c in mot if unicodedata.category(c) != "Mn")


def mots_pleins(texte: str) -> set[str]:
    bruts = re.findall(r"[a-zA-ZÀ-ÿ]{3,}", texte)
    return {m for m in (_normalise(b) for b in bruts) if m not in MOTS_VIDES}


def decoupe_propositions(texte: str, attendu: int) -> list[str]:
    """Decoupe la reponse en propositions numerotees. Repli : decoupage par
    paragraphes doubles si aucune numerotation n'est trouvee."""
    marques = list(MOTIF_BLOC.finditer(texte))
    # on ne garde que la premiere occurrence de chaque numero, dans l'ordre
    debuts: list[int] = []
    vus: set[str] = set()
    for m in marques:
        num = m.group(1)
        if num in vus or num == "0":
            continue
        vus.add(num)
        debuts.append(m.start())
    if len(debuts) >= 2:
        debuts.append(len(texte))
        return [texte[debuts[i] : debuts[i + 1]].strip() for i in range(len(debuts) - 1)]
    blocs = [b.strip() for b in re.split(r"\n\s*\n", texte) if len(b.strip()) > 80]
    return blocs[:attendu] if blocs else [texte]


def diversite_lexicale(propositions: list[str]) -> float:
    ensembles = [mots_pleins(p) for p in propositions]
    ensembles = [e for e in ensembles if e]
    if len(ensembles) < 2:
        return 0.0
    similarites = []
    for a, b in itertools.combinations(ensembles, 2):
        union = a | b
        if not union:
            continue
        similarites.append(len(a & b) / len(union))
    if not similarites:
        return 0.0
    return 1.0 - (sum(similarites) / len(similarites))


GABARIT_ECART = """Tu mesures l'ECART entre des directions creatives proposees par
un modele. Tu ne juges pas laquelle est la meilleure, ni si elles sont bonnes.

COMMANDE PASSEE AU MODELE
{question}

CONTRAINTE DE L'EPREUVE
{critere}

GRILLE
{rubrique}

PROPOSITIONS A EXAMINER
{reponse}

Deux directions sont distinctes si elles changent au moins l'un de ces trois axes :
le dispositif (comment on filme ou on fabrique), le point de vue (qui regarde,
depuis ou), le materiau (avec quoi c'est fait). Changer le sujet de surface en
gardant le meme dispositif n'est PAS une direction distincte.

Deux phrases nommant les redondances que tu vois, puis, derniere ligne :
NOTE: <0, 1, 2 ou 3>
"""


@scorer(metrics=[mean(), stderr()])
def ecart_propositions(juges: list[str], attendu: int = 5) -> Scorer:
    async def score(state: TaskState, target: Target) -> Score:
        reponse = state.output.completion
        propositions = decoupe_propositions(reponse, attendu)
        lexical = diversite_lexicale(propositions)

        invite = GABARIT_ECART.format(
            question=state.input_text,
            critere=target.text,
            rubrique=charge_rubrique("creation-ecart"),
            reponse=reponse,
        )
        retenue, meta = await vote_jury(juges, invite)

        meta["nb_propositions_detectees"] = len(propositions)
        meta["diversite_lexicale"] = round(lexical, 3)
        meta["longueurs"] = [len(p) for p in propositions]
        if retenue is None:
            return Score(value=float("nan"), explanation="aucun juge exploitable", metadata=meta)

        meta["note_jury_sur_3"] = retenue
        valeur = 0.6 * (retenue / 3.0) + 0.4 * lexical
        # sanction si le modele n'a pas rendu le nombre demande
        if len(propositions) < attendu:
            manque = (attendu - len(propositions)) / attendu
            meta["sanction_nombre"] = round(manque, 3)
            valeur *= 1.0 - manque
        return Score(
            value=round(valeur, 4),
            answer=reponse[:400],
            explanation=(
                f"jury {retenue}/3, lexical {lexical:.2f}, "
                f"{len(propositions)}/{attendu} propositions"
            ),
            metadata=meta,
        )

    return score
