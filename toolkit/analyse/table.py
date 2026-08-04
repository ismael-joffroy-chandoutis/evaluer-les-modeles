"""Tableau de resultats + test de saturation.

Usage : python analyse/table.py logs/

Produit :
  1. le tableau categorie x modele (moyenne des notes normalisees 0-1) ;
  2. le tableau epreuve x modele, qui est le seul utile pour router ;
  3. le test de saturation : etendue des scores et taux d'items ou tous les
     modeles obtiennent la note maximale. C'est la mesure qui dit si la
     notation par grille discrimine encore ou s'il faut passer aux duels ;
  4. l'accord du jury : part d'items unanimes, dispersion moyenne, separement
     pour les dimensions verifiables et pour les dimensions de gout.
"""

from __future__ import annotations

import glob
import statistics
import sys
from collections import defaultdict
from pathlib import Path

from inspect_ai.log import read_eval_log

# Ce qui est verifiable (l'accord doit etre eleve) et ce qui est du gout
# (la dispersion est une donnee, pas un defaut).
EPREUVES_GOUT = {"tenue de la voix", "ecart entre propositions", "la duree comme decision"}


def charge(dossier: str) -> list[dict]:
    lignes = []
    for f in sorted(glob.glob(str(Path(dossier) / "*.eval"))):
        log = read_eval_log(f)
        if log.status != "success" or not log.samples:
            print(f"  (ignore : {Path(f).name}, statut {log.status})", file=sys.stderr)
            continue
        modele = log.eval.model.split("/", 1)[-1]
        for s in log.samples:
            sc = list(s.scores.values())[0]
            meta = sc.metadata or {}
            lignes.append(
                {
                    "modele": modele,
                    "tache": log.eval.task.split("/")[-1],
                    "item": str(s.id),
                    "epreuve": meta.get("epreuve", ""),
                    "valeur": float(sc.value) if sc.value == sc.value else None,
                    "unanime": meta.get("unanime"),
                    "dispersion": meta.get("dispersion"),
                    "notes": meta.get("notes_par_juge", {}),
                }
            )
    return lignes


def tableau(lignes: list[dict], cle: str) -> None:
    modeles = sorted({l["modele"] for l in lignes})
    cles = sorted({l[cle] for l in lignes})
    largeur = max(len(str(k)) for k in cles) + 2
    print("\n" + " " * largeur + "".join(f"{m[:22]:>24}" for m in modeles))
    for k in cles:
        cellules = []
        for m in modeles:
            vals = [l["valeur"] for l in lignes if l[cle] == k and l["modele"] == m and l["valeur"] is not None]
            cellules.append(f"{statistics.mean(vals):>24.2f}" if vals else f"{'-':>24}")
        print(f"{str(k):<{largeur}}" + "".join(cellules))
    cellules = []
    for m in modeles:
        vals = [l["valeur"] for l in lignes if l["modele"] == m and l["valeur"] is not None]
        cellules.append(f"{statistics.mean(vals):>24.2f}" if vals else f"{'-':>24}")
    print(f"{'TOTAL':<{largeur}}" + "".join(cellules))


def saturation(lignes: list[dict]) -> None:
    print("\n=== TEST DE SATURATION ===")
    modeles = sorted({l["modele"] for l in lignes})
    par_item: dict[str, list[float]] = defaultdict(list)
    for l in lignes:
        if l["valeur"] is not None:
            par_item[l["item"]].append(l["valeur"])
    complets = {i: v for i, v in par_item.items() if len(v) == len(modeles)}
    if not complets:
        print("pas assez de runs pour tester la saturation")
        return
    plafonnes = [i for i, v in complets.items() if min(v) >= 1.0]
    etendues = [max(v) - min(v) for v in complets.values()]
    moyennes = [statistics.mean([l["valeur"] for l in lignes if l["modele"] == m and l["valeur"] is not None]) for m in modeles]
    print(f"items comparables            : {len(complets)}")
    print(f"items ou TOUS sont au maximum: {len(plafonnes)} ({100*len(plafonnes)/len(complets):.0f} %)")
    print(f"etendue moyenne par item     : {statistics.mean(etendues):.2f} (0 = indiscernable)")
    print(f"etendue des moyennes modeles : {max(moyennes)-min(moyennes):.2f}")
    print(f"ecart type entre modeles     : {statistics.pstdev(moyennes):.3f}")
    for i, v in sorted(complets.items(), key=lambda kv: max(kv[1]) - min(kv[1]), reverse=True)[:5]:
        print(f"  item le plus discriminant : {i:<24} etendue {max(v)-min(v):.2f}")


def accord_jury(lignes: list[dict]) -> None:
    print("\n=== ACCORD DU JURY ===")
    for etiquette, filtre in (
        ("verifiable", lambda l: l["epreuve"] not in EPREUVES_GOUT),
        ("gout      ", lambda l: l["epreuve"] in EPREUVES_GOUT),
    ):
        sel = [l for l in lignes if filtre(l) and l["notes"]]
        if not sel:
            continue
        unan = sum(1 for l in sel if l["unanime"]) / len(sel)
        disp = statistics.mean([l["dispersion"] for l in sel if l["dispersion"] is not None])
        print(f"{etiquette} : {len(sel):>3} jugements, unanimite {100*unan:>3.0f} %, dispersion moyenne {disp:.2f}/3")


if __name__ == "__main__":
    dossier = sys.argv[1] if len(sys.argv) > 1 else "logs"
    lignes = charge(dossier)
    if not lignes:
        sys.exit("aucun log exploitable")
    print(f"{len(lignes)} jugements charges depuis {dossier}")
    print("\n=== PAR CATEGORIE ===")
    tableau(lignes, "tache")
    print("\n=== PAR EPREUVE ===")
    tableau(lignes, "epreuve")
    saturation(lignes)
    accord_jury(lignes)
