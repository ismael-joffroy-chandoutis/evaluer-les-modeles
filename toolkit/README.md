# Banc d'essai d'atelier

Implementation executable du protocole decrit dans
[banc-d-essai-atelier.md](https://github.com/ismael-joffroy-chandoutis/evaluer-les-modeles).

Ce depot ne contient pas un banc d'essai. Il contient la mecanique d'un banc
d'essai, plus une quinzaine d'items d'exemple pour verifier qu'elle tourne.
Les items qui comptent sont les votres, et ils restent chez vous.

Ce qui est ici et qui n'existe pas ailleurs :

- **le refus argumente** : on soumet une direction creative faible en demandant
  de l'executer ; qui execute sans rien dire perd, qui signale gagne, qui
  refuse en argumentant gagne le plus ;
- **l'ecart entre propositions** : on demande cinq directions et on mesure leur
  distance, pas leur qualite ;
- **le jury hors famille** : le jury est recompose pour chaque candidat, de
  sorte qu'aucun modele n'est jamais juge par sa propre famille ;
- **le desaccord conserve** : les notes de chaque juge restent dans le journal,
  l'unanimite et la dispersion sont mesurees separement sur le verifiable et
  sur le gout.

---

## Installation

```bash
git clone <ce depot> && cd toolkit
export OPENROUTER_API_KEY=sk-or-...
./run.sh install
```

Sortie reelle de `./run.sh install` (extrait) :

```
Using CPython 3.12.9
Creating virtual environment at: .venv
creation.jsonl : 6 items
admin_juridique.jsonl : 4 items
recherche.jsonl : 4 items
0.3.251
```

Python 3.12 exactement si vous voulez aussi YourBench (`requires_python
<3.13,>=3.12`). Inspect AI seul accepte plus large.

## Lancer

```bash
./run.sh un openrouter/anthropic/claude-sonnet-5      # un modele, trois taches
./run.sh tous                                          # les quatre modeles
./run.sh table                                         # tableau + saturation
./run.sh logs                                          # visualiseur Inspect
```

Une categorie seule :

```bash
.venv/bin/inspect eval banc/tasks/creation.py \
  --model openrouter/anthropic/claude-sonnet-5 \
  -T candidat=openrouter/anthropic/claude-sonnet-5 \
  --log-dir logs --message-limit 4 --token-limit 12000 --time-limit 300
```

Le parametre `-T candidat=` n'est pas decoratif : c'est lui qui permet
d'exclure la famille du modele evalue du jury. Sans lui, la tache refuse de
demarrer plutot que de composer un jury contamine.

## Ce que ca rend

Sortie reelle de `./run.sh table` apres un cycle complet (quatre modeles,
quatorze items, jury de trois juges par candidat) :

```
=== PAR CATEGORIE ===
                   anthropic/claude-sonne  google/gemini-3.6-flas  mistralai/mistral-medi    openai/gpt-5.6-terra
admin_juridique                      1.00                    0.42                    0.17                    0.67
creation                             0.61                    0.54                    0.40                    0.61
recherche                            0.83                    0.75                    0.58                    0.92
TOTAL                                0.78                    0.57                    0.38                    0.71

=== TEST DE SATURATION ===
items comparables            : 14
items ou TOUS sont au maximum: 0 (0 %)
etendue moyenne par item     : 0.45 (0 = indiscernable)
etendue des moyennes modeles : 0.40

=== ACCORD DU JURY ===
verifiable :  44 jugements, unanimite  50 %, dispersion moyenne 0.57/3
gout       :  12 jugements, unanimite  17 %, dispersion moyenne 1.00/3
```

Le tableau par categorie ne sert a rien tout seul. Celui qui sert est le
tableau par epreuve, que `run.sh table` imprime juste apres : c'est lui qui
dit qui appeler pour quoi.

## Architecture

```
banc/
  jury.py                 compose un jury hors famille pour chaque candidat
  scorers/rubrique.py     grille 0-3 a ancrages, vote majoritaire, dispersion gardee
  scorers/refus.py        refus argumente, avec son item temoin inverse
  scorers/ecart.py        ecart entre propositions : jury + mesure lexicale
  tasks/creation.py       les six epreuves de creation
  tasks/admin_juridique.py
  tasks/recherche.py
  tasks/agentique.py      budget d'erreur : un EDL a faire accepter par un outil
rubriques/                neuf grilles a ancrages concrets, en markdown
items/                    items d'exemple + le mode d'emploi pour les remplacer
analyse/table.py          tableaux, test de saturation, accord du jury
yourbench/                config locale pour fabriquer du volume ancre
harbor/                   une tache a verification objective, prete a tourner
```

## Le jury

`model_graded_qa` d'Inspect accepte nativement une liste de juges et reduit par
vote majoritaire. Verifie dans le code de la version 0.3.251 :

```python
    assert isinstance(model, list)
    scorers = [get_scorer(model) for model in model]
    return multi_scorer(scorers, "mode")
```

Ce que cette fonction ne fait pas : exclure la famille du modele evalue, et
conserver le desaccord entre juges. Les deux manquent au protocole, donc les
scorers de `banc/scorers/` refont le tour de jury eux-memes : ils appellent les
juges en parallele, votent par le mode, et rangent dans la metadonnee du score
les notes individuelles, l'unanimite, l'ecart type et les incidents.

Extrait reel du journal, pour un item :

```json
{"notes_par_juge": {"openrouter/openai/gpt-5.4-mini": 2,
                    "openrouter/anthropic/claude-sonnet-5": 2,
                    "openrouter/qwen/qwen3.7-plus": 2},
 "dispersion": 0, "unanime": true, "note_brute_sur_3": 2.0,
 "rubrique": "recherche-fidelite"}
```

## Budget d'erreur

```bash
.venv/bin/inspect eval banc/tasks/agentique.py --model M -T candidat=M --message-limit 6  --epochs 3
.venv/bin/inspect eval banc/tasks/agentique.py --model M -T candidat=M --message-limit 24 --epochs 3
```

Le modele doit faire accepter un EDL CMX3600 par un outil qui valide
strictement et renvoie des erreurs precises. Pas de conteneur, pas de reseau :
le meme test tourne partout. Un modele qui reussit a 24 messages et echoue a 6
ne sait pas faire la tache, il sait se rattraper.

Resultat reel, quatre modeles, trois essais chacun :

| modele | budget 24 | depots | budget 6 | depots |
|---|---|---|---|---|
| claude-sonnet-5 | 3/3 | 1 a 2 | 3/3 | 1 a 2 |
| gpt-5.6-terra | 3/3 | 1 | 3/3 | 1 |
| gemini-3.6-flash | 3/3 | 1 | 3/3 | 1 |
| mistral-medium-3-5 | 3/3 | 5, 6, 7 | **0/3** | 2 (plafond atteint) |

En budget large les quatre modeles sont a egalite parfaite. En budget serre,
le quatrieme tombe a zero. C'est le meme modele, la meme tache, et deux
conclusions opposees selon le reglage du harnais.

## Vraie verification objective : Harbor

`harbor/fidelite-timeline/` est une tache complete : un CSV de plans, un FCPXML
a produire, sept tests qui parsent le fichier et comparent des nombres. La
contrainte du protocole y est encodee en dur : aucun plan ne doit etre
raccourci, meme long.

La solution de reference passe les tests, verifie hors conteneur :

```
$ HARBOR_APP=$(pwd) python -m pytest tests/test_outputs.py -q
.......                                                                  [100%]
7 passed in 0.04s
```

Faire tourner un agent dessus demande Docker :

```
$ harbor run --agent nop --env docker
Docker is not installed or not on PATH. Please install Docker and try again.
```

## Fabriquer du volume : YourBench

```bash
../.venv-yb/bin/yourbench run yourbench/config.yaml
```

Rien ne part sur le Hub (`push_to_hub: false`). Sortie reelle sur un document
de 484 mots :

```
Stage Timing:
  Document Ingestion: 67.25s (77%)
  Summarization: 8.05s (9%)
  Chunking: 0.47s (1%)
  Single-Hop Questions: 11.48s (13%)
  Total: 87.25s
Saved 28 single-shot questions
```

Vingt-huit questions pour 484 mots : le rendement est reel, la redondance
aussi. Les questions generees sont extractives et se recouvrent largement. Il
faut relire, ce qui est exactement ce que la documentation de l'outil annonce.

## Limites connues

- Un jeu prive n'est pas reproductible. Ses resultats ne valent que pour celui
  qui l'a construit.
- Le jury de modeles ne remplace pas le juge humain sur les dimensions de gout.
  La dispersion mesuree ici est de 1,00 point sur 3 entre juges sur ces
  dimensions, contre 0,57 sur le verifiable. Le chiffre dit exactement combien
  il faut se mefier.
- La mesure d'ecart entre propositions punit la redondance, pas la betise. Sans
  un item de qualite note a cote, un modele qui repond n'importe quoi la gagne.
- Les duels en aveugle avec classement Elo, prevus par le protocole pour les
  dimensions de gout, ne sont pas implementes ici.

## Licence

MIT pour le code. Les items d'exemple sont des exemples : ne les utilisez pas
comme mesure.
