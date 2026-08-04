# Les items

## La regle

**L'outil est partage, les items ne le sont pas.** Les fichiers presents ici
sont des exemples, ecrits pour que le banc tourne chez quelqu'un qui vient de
cloner le depot. Ils ne mesurent pas votre travail, ils mesurent qu'il y a du
courant dans les fils.

Un jeu d'epreuves publie finit statistiquement dans les donnees
d'entrainement. Le votre doit rester prive, et il doit etre tire de travail
que vous avez reellement fait.

## Format

Un objet JSON par ligne. Champs :

| champ | obligatoire | role |
|---|---|---|
| `id` | oui | identifiant stable, sert a comparer les runs entre eux |
| `input` | oui | l'enonce, tel qu'il est envoye au modele |
| `critere` | oui | ce qu'on attend, lu par le jury, jamais par le modele evalue |
| `type` | oui | `rubrique`, `refus` ou `ecart` (choisit la mecanique de notation) |
| `rubrique` | pour `rubrique` | nom d'un fichier de `rubriques/`, sans `.md` |
| `epreuve` | non | libelle affiche dans le tableau de resultats |
| `direction_valable` | pour `refus` | `true` si la direction soumise est BONNE (item temoin) |

Exemple minimal :

```json
{"id": "crea-refus-12", "type": "refus", "epreuve": "refus argumente", "input": "...", "critere": "...", "direction_valable": false}
```

## Remplacer les items par les siens

1. ecrire ses items dans `items/creation.jsonl`, `items/admin_juridique.jsonl`,
   `items/recherche.jsonl`. Rien d'autre a modifier : les taches lisent ces
   fichiers par leur nom.
2. garder les fichiers hors du depot public :

```
echo "items/*.jsonl" >> .gitignore
git rm --cached items/*.jsonl
```

3. compter une dizaine d'items par categorie pour commencer. Le protocole vise
   cent a cent cinquante items a terme, dont un tiers renouvele chaque annee
   avec du materiau posterieur a la derniere coupure d'entrainement connue.

## Ce qui fait un bon item

- il vient d'une decision reelle, pas d'un exercice ;
- on sait dire ce qu'une mauvaise reponse ressemble, pas seulement une bonne ;
- le `critere` contient la reponse ou le comportement attendu de facon assez
  precise pour qu'un juge qui ne connait pas le dossier puisse trancher ;
- il ne cite ni nom de personne, ni donnee personnelle, ni piece confidentielle
  si le jeu doit un jour circuler.

## Les items temoins

Deux epreuves de ce banc peuvent etre gagnees par un comportement stupide :

- le **refus argumente** est gagne par un modele qui objecte a tout ;
- l'**ecart entre propositions** est gagne par un modele qui repond n'importe
  quoi, puisque n'importe quoi est divers.

Il faut donc au moins un item temoin par epreuve : pour le refus, une commande
saine ou objecter coute des points (`direction_valable: true`, rubrique
`creation-refus-temoin`) ; pour l'ecart, un item ou la qualite est notee
separement, avec la rubrique `creation-voix` ou une rubrique maison.
Sans ces temoins, les deux mesures sont truquees.

## Ne jamais modifier une version figee

Corriger la notation d'un banc en cours de route produit des scores qui ne
sont plus comparables entre eux. On date le jeu, on le fige, et une correction
donne une nouvelle version datee.
