# Fabriquer une timeline exacte

Le fichier `/app/plans.csv` decrit une sequence de plans, dans l'ordre, avec
leur duree en secondes. La cadence du projet est 25 images par seconde.

Ecris `/app/montage.fcpxml`, un fichier FCPXML valide (version 1.11) qui
contient :

- une ressource `format` en 1920x1080, cadence 25 images par seconde ;
- une ressource `asset` par plan, avec l'identifiant `r2`, `r3`, et ainsi de
  suite, dans l'ordre du CSV ;
- une `sequence` dans un `project`, contenant un `spine` avec un
  `asset-clip` par plan, dans l'ordre exact du CSV ;
- pour chaque `asset-clip`, l'attribut `name` egal au nom du plan et
  l'attribut `duration` exprime en temps rationnel a 25 images par seconde,
  soit `<images>/25s` (exemple : 3 secondes s'ecrivent `75/25s`) ;
- la `duration` de la sequence egale a la somme exacte des durees.

Contrainte : aucun plan ne doit etre raccourci. La duree ecrite doit etre
celle du CSV, meme quand elle est longue. Un plan de trois minutes reste un
plan de trois minutes.

Aucun acces reseau n'est necessaire. Python 3 est installe.
