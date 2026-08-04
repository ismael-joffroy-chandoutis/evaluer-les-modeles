"""Verification objective de la timeline produite.

Rien ici ne juge le style : on parse le fichier et on compare des nombres.
C'est exactement ce que Harbor sait faire et qu'un jury de modeles ne devrait
jamais avoir a faire.
"""

import csv
import os
import xml.etree.ElementTree as ET
from pathlib import Path

# `HARBOR_APP` permet de rejouer ces tests hors conteneur, avec la meme
# logique exactement. Dans l'environnement Harbor, la valeur par defaut suffit.
RACINE = Path(os.environ.get("HARBOR_APP", "/app"))
SORTIE = RACINE / "montage.fcpxml"
PLANS = RACINE / "plans.csv"
FPS = 25


def plans_attendus():
    with PLANS.open() as f:
        return [(r["nom"], int(r["duree_secondes"])) for r in csv.DictReader(f)]


def test_fichier_present():
    assert SORTIE.exists(), "montage.fcpxml absent"
    assert SORTIE.stat().st_size > 0, "montage.fcpxml vide"


def test_xml_parsable():
    ET.parse(SORTIE)


def test_format_du_projet():
    racine = ET.parse(SORTIE).getroot()
    fmt = racine.find(".//format")
    assert fmt is not None, "aucune ressource format"
    assert fmt.get("width") == "1920"
    assert fmt.get("height") == "1080"
    assert fmt.get("frameDuration") in ("1/25s", "100/2500s")


def test_un_clip_par_plan_dans_l_ordre():
    racine = ET.parse(SORTIE).getroot()
    clips = racine.findall(".//spine/asset-clip")
    attendus = plans_attendus()
    assert len(clips) == len(attendus), f"{len(clips)} clips pour {len(attendus)} plans"
    for clip, (nom, _) in zip(clips, attendus):
        assert clip.get("name") == nom, f"attendu {nom}, trouve {clip.get('name')}"


def test_durees_exactes_aucun_plan_raccourci():
    racine = ET.parse(SORTIE).getroot()
    clips = racine.findall(".//spine/asset-clip")
    for clip, (nom, secondes) in zip(clips, plans_attendus()):
        attendu = f"{secondes * FPS}/{FPS}s"
        assert clip.get("duration") == attendu, (
            f"{nom} : duree {clip.get('duration')} au lieu de {attendu}"
        )


def test_duree_totale_de_la_sequence():
    racine = ET.parse(SORTIE).getroot()
    seq = racine.find(".//sequence")
    assert seq is not None, "aucune sequence"
    total = sum(d for _, d in plans_attendus()) * FPS
    assert seq.get("duration") == f"{total}/{FPS}s"


def test_assets_numerotes():
    racine = ET.parse(SORTIE).getroot()
    ids = [a.get("id") for a in racine.findall(".//asset")]
    assert ids == [f"r{i + 2}" for i in range(len(plans_attendus()))], ids
