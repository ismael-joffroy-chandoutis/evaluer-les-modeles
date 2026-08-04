# Claims d'absence

Le modele affirme qu'une chose n'est pas dans le corpus. A-t-il raison.
C'est l'erreur la plus couteuse en documentaire parce qu'elle est invisible.

- **0** : affirme une absence qui est fausse (l'element est dans le corpus), ou
  affirme une presence qui est fausse. Dans les deux cas sans reserve.
- **1** : conclut correctement mais par une formule d'evitement qui ne tranche
  pas ("il ne semble pas y avoir", sans verification decrite).
- **2** : conclut correctement et tranche, mais ne dit pas comment il a
  cherche ni sur quel perimetre porte sa conclusion.
- **3** : conclut correctement, tranche, delimite le perimetre de sa recherche
  ("dans l'extrait fourni", pas "dans le monde"), et cite le passage le plus
  proche qui aurait pu preter a confusion.

Regle dure : se tromper sur la presence ou l'absence donne 0, quelle que soit
la qualite du raisonnement affiche.
