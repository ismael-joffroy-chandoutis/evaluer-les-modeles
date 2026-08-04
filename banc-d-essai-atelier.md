# Un banc d'essai depuis l'atelier

*Proposition de protocole d'évaluation des modèles, écrite depuis une pratique de création plutôt que depuis un laboratoire.*

---

## De quoi il s'agit

Un banc d'essai, en apprentissage automatique, est une série d'épreuves standardisées que l'on fait passer à des modèles pour les comparer. Les plus connus sont publics : MMLU pour les connaissances, SWE-bench pour la programmation, les arènes de préférence où deux réponses anonymes sont soumises au vote. Leurs scores servent d'argument commercial le jour où un modèle sort, et de boussole au reste du monde pour choisir quel modèle utiliser.

Le texte qui suit part d'un constat simple : ces scores ne disent rien d'utile à quelqu'un qui fabrique des œuvres avec ces modèles. Non parce qu'ils seraient mal faits, mais parce qu'ils mesurent autre chose. Il propose donc un protocole de rechange, conçu pour une pratique artistique qui travaille avec des agents, et qui a aussi besoin de ces modèles pour du code, de l'administratif, du juridique et de la recherche documentaire. Ce protocole n'est pas un instrument scientifique et ne prétend pas l'être : sa validité est locale par construction, et c'est précisément ce qui le rend utile là où les instruments universels ne disent rien.

## Pourquoi les classements publics ne servent à rien ici

Trois faits, tous documentés en 2025 et 2026, suffisent à fermer le débat.

Le premier vient de l'audit le plus large mené sur le sujet, *Measuring what Matters: Construct Validity in Large Language Model Benchmarks* (Bean et al., NeurIPS 2025) : sur quatre cent quarante-cinq bancs d'essai examinés en détail par vingt-neuf experts, **seize pour cent** utilisent des estimations d'incertitude ou des tests statistiques. Le reste publie des scores sans marge d'erreur. Un second audit, présenté à FAccT 2026, ajoute que **soixante-trois pour cent** des bancs d'essai mis en avant ne sont utilisés que par un seul constructeur de modèles. Une part massive de l'écosystème d'évaluation est du marketing sur mesure.

Le deuxième concerne le goût, et il vient du benchmark TASTE (Zhu et al., 2026). Deux cohortes disjointes de cinq designers professionnels chacune ont classé les sorties des principaux générateurs d'images sur neuf critères, de la typographie à la hiérarchie visuelle. Il y a bien un signal de préférence professionnelle, robuste, qui rejette l'hypothèse du hasard sur les neuf critères. Mais **aucun système automatique d'évaluation esthétique ne dépasse 0,55 d'accord** avec ce consensus, le meilleur étant à peine au-dessus du tirage au sort. Et les plus gros modèles de vision ne font pas mieux : le problème n'est pas l'échelle, il est structurel. Les métriques esthétiques sur lesquelles toute l'industrie s'appuie ne mesurent pas le goût.

Le troisième est le plus intéressant pour un artiste, et il vient du Human Creativity Benchmark publié par Contra Labs en juin 2026, quinze mille jugements de professionnels sur cinq domaines créatifs. C'est le seul travail qui refuse de traiter le désaccord entre évaluateurs comme du bruit : il sépare explicitement deux zones, la convergence se concentrant sur les dimensions vérifiables (justesse technique, hiérarchie visuelle), la divergence sur les dimensions de goût (direction esthétique, prise de risque conceptuelle). Écraser les deux en une seule note détruit précisément l'information qui compte : où le modèle doit être **exact**, et où il doit être **pilotable**.

À quoi s'ajoute une dérive qu'aucun classement grand public ne pénalise : l'homogénéisation. La diversité marginale de chaque texte supplémentaire produit par un modèle décroît plus vite que chez les humains, et les arènes de préférence récompensent structurellement la complaisance. Un modèle qui donnerait toujours la même bonne réponse dominerait les classements de créativité existants. Pour quelqu'un dont le métier est l'écart, c'est disqualifiant.

Conclusion : il n'y a pas de banc d'essai à choisir, il y en a un à construire. Et Clémentine Fourrier, qui a dirigé l'effort d'évaluation de Hugging Face entre 2023 et 2025 et signé son *LLM Evaluation Guidebook*, le dit dans les mêmes termes : les classements publics ne mesurent pas une capacité générale, seule compte une évaluation spécifique au cas d'usage réel.

---

## Le banc d'essai que je construirais si je n'avais aucune contrainte

Avant de descendre dans ton atelier, la réponse générale, parce qu'elle éclaire l'autre.

Si je pouvais imposer une seule évaluation au champ, ce ne serait ni un examen de connaissances ni un concours de code. Ce serait une **mesure de la collaboration longue**. Prendre une personne, un projet réel, six mois, et mesurer trois choses qu'aucun instrument actuel ne regarde.

La première est la tenue d'une décision. Un modèle se souvient-il, trois semaines plus tard, qu'on a écarté une direction et pourquoi, sans qu'on ait à le lui rappeler, et sans qu'il la repropose habillée autrement. Les mesures actuelles portent sur des horizons de tâches, jamais sur des horizons de relation.

La deuxième est le refus argumenté. Aucun dispositif d'évaluation ne récompense un modèle qui dit « cette direction est faible, voici pourquoi » plutôt que d'exécuter. Les arènes de préférence récompensent l'inverse, et la complaisance qui en résulte est documentée. Or dans un travail réel, le désaccord utile a plus de valeur que dix exécutions dociles.

La troisième est la non-régression du jugement humain. Est-ce que travailler avec ce modèle rend meilleur, ou seulement plus rapide. C'est mesurable : on fait juger à l'aveugle, par des pairs, du travail produit avec et sans, à six mois d'intervalle. C'est le seul test qui répond à la question qui compte, et personne ne le fait parce qu'il est lent, cher, et qu'il ne produit pas un chiffre publiable le jour de la sortie d'un modèle.

Ce banc d'essai idéal est irréaliste pour un laboratoire. Il est parfaitement réaliste pour une personne seule, sur sa propre pratique. C'est exactement ce que la suite décrit.

---

## Le principe : évaluer par phase, pas par domaine

L'erreur des grilles existantes est de découper par domaine (écriture, code, image) alors que le travail se découpe par **phase**, et que la même personne attend des choses opposées d'une phase à l'autre.

En phase d'exploration, je veux de la divergence : dix pistes dont huit mauvaises valent mieux qu'une piste correcte. En phase de décision, je veux de la contradiction : qu'on me dise ce qui ne va pas. En phase d'exécution, je veux de la fidélité exacte et zéro initiative. En phase de vérification, je veux de la paranoïa. En phase de finition, je veux de la sobriété.

Un modèle qui excelle partout n'existe pas et n'est pas souhaitable : la divergence en phase d'exécution s'appelle une erreur, la fidélité en phase d'exploration s'appelle une impasse. **Donc pas de note globale. Cinq profils, et un modèle est bon pour une phase, pas dans l'absolu.** C'est la seule structure qui produise une décision utile : quel modèle j'appelle à quel moment.

Cette structure a un effet secondaire qui me plaît : elle rend le classement inutilisable comme argument de vente. On ne peut pas en tirer un chiffre unique pour une page produit.

---

## Les cinq catégories d'usage, et ce qu'on y mesure vraiment

### 1. Création

C'est là que tout se joue et que rien n'est mesuré. Quatre épreuves.

**La proposition écartée.** On donne une matière réelle et une contrainte, on demande cinq directions. On ne note pas la meilleure, on note **l'écart entre elles** et le nombre de directions qu'on n'aurait pas trouvées seul. Un modèle qui rend cinq variantes de la même idée échoue, même si l'idée est bonne. C'est la mesure anti-homogénéisation qui manque partout.

**La tenue de la voix.** Trois textes courts dans une voix donnée, jugés en aveugle par quelqu'un qui connaît cette voix, mélangés à des textes authentiques. On mesure le taux de détection et, plus utile, **la nature des ratés** : qu'est-ce que la machine surjoue, qu'est-ce qu'elle lisse. Pour ma pratique, le raté typique est connu : l'essai poli générique, la sur-justification, l'emphase.

**Le refus.** On soumet volontairement une direction faible en demandant de l'exécuter. Le modèle qui exécute proprement perd des points. Celui qui exécute en signalant le problème gagne. Celui qui refuse et argumente gagne le plus. C'est la mesure directe de la complaisance, et elle est absente de tous les bancs d'essai existants.

**La durée.** Sur du matériau audiovisuel : est-ce que le modèle comprend qu'un plan tenu longtemps est une décision et non une erreur. Aucun banc d'essai vidéo ne mesure la tenue, l'attente, le silence, le hors-champ. Ils mesurent le mouvement et l'appellent esthétique dynamique. C'est le trou le plus spécifique à un cinéma d'auteur, et il est béant.

### 2. Montage et matière audiovisuelle

Les instruments récents ont enfin été construits avec des professionnels, et le résultat est instructif : dès qu'on ancre l'évaluation dans le langage cinématographique plutôt que dans la qualité d'image, **les scores s'effondrent et rien ne sature**, en particulier sur les séquences à plusieurs plans. C'est la confirmation que le mur n'est pas dépassé.

Ce que j'ajoute et qui n'existe nulle part : **la fidélité au capté**. Étant donné une matière documentaire réelle, le modèle sait-il distinguer ce qui a été filmé de ce qui est plausible, et refuse-t-il de combler un manque quand le manque est le sujet. Aucune métrique ne distingue une image plausible d'une image vraie. C'est le cœur de mon travail et le point aveugle absolu du champ.

### 3. Code

Ici les instruments publics existent et sont bons, mais ils mesurent le mauvais objet pour moi. Je n'écris pas du logiciel, je fabrique des outils d'atelier qui doivent survivre à leur auteur pendant deux ans. Les trois épreuves qui comptent : est-ce que ça tourne encore après une mise à jour du système ; est-ce que je peux relire et modifier six mois plus tard ; est-ce que le modèle a signalé ce qu'il ne savait pas au lieu d'inventer une dépendance. La troisième est la seule qui prédise vraiment le coût futur.

### 4. Administratif et juridique français

La catégorie la plus ingrate et la plus utile, parce qu'elle est **vérifiable**. Un dossier de subvention, une déclaration, un contrat de cession de droits, une convention de coproduction : il existe une bonne réponse, ou au moins des réponses fausses identifiables. Trois mesures : l'exactitude factuelle sur du droit français réel (dispositifs, seuils, formulaires), le taux d'invention confiante, et surtout **le taux de signalement d'incertitude**. Un modèle qui dit « ce point relève d'un conseil, voici les deux lectures possibles » vaut infiniment mieux qu'un modèle qui tranche bien neuf fois sur dix et se trompe avec aplomb la dixième. Dans cette catégorie, l'erreur coûte de l'argent réel.

Cette catégorie est aussi la meilleure sentinelle du système entier : c'est la seule où je peux constater objectivement qu'un modèle a régressé.

### 5. Recherche et lecture

Face à un corpus réel, en français comme en anglais : est-ce que le modèle rapporte ce que la source dit, ou ce que j'espérais qu'elle dise. Épreuve décisive, celle des **claims d'absence** : quand il affirme qu'une chose n'existe pas dans un corpus, a-t-il raison. C'est l'erreur la plus coûteuse dans un travail de documentaire, parce qu'elle est invisible.

---

## Le protocole, concrètement

**Le jeu d'épreuves reste privé.** C'est non négociable et c'est la seule défense réelle contre la contamination : tout banc d'essai public finit statistiquement dans les données d'entraînement. Le modèle à suivre est celui de Meta pour Llama 3 : mille huit cents prompts couvrant douze cas d'usage, dont l'écriture créative et l'incarnation de personnage, **tenus hors d'accès même des équipes internes de modélisation**. À mon échelle : cent à cent cinquante épreuves tirées de travail réellement fait, jamais publiées, dont un tiers renouvelé chaque année avec des matériaux postérieurs à la dernière coupure d'entraînement connue.

**La notation combine deux régimes.** Une grille à ancrages concrets pour les dimensions vérifiables, et des **duels en aveugle avec classement Elo** pour les dimensions de goût, parce que la notation absolue sature dès que tous les modèles deviennent bons. Position randomisée, longueur normalisée, verbosité pénalisée.

**Le jury est multi-familles.** Jamais un juge de la même famille que le modèle jugé : l'auto-préférence est documentée partout, et la parade éprouvée est un ensemble de juges issus de familles différentes. Pour les dimensions de goût, le juge reste humain, c'est-à-dire moi, en aveugle, ce qui suppose un dispositif qui masque vraiment l'origine des sorties.

**Le désaccord est conservé, pas moyenné.** Deux mesures séparées : l'accord sur le vérifiable, qui doit être élevé, et la dispersion sur le goût, qui est une donnée et non un défaut. Un modèle qui polarise n'est pas mauvais, il est spécialisé.

**Ce qui est mesuré ne s'arrête pas au résultat.** Pour tout ce qui est agentique : le nombre de tours, le coût en jetons, les erreurs d'outil, et surtout la **récupération après erreur**. Un résultat récent l'a montré de façon décisive : deux modèles peuvent afficher le même taux de réussite alors que l'un produit deux fois et demie plus d'erreurs, simplement parce que l'environnement de test lui laissait dix chances de se rattraper. En resserrant le budget d'erreur, l'écart réapparaît. Donc : **budget d'erreur serré, sinon on mesure la tolérance du harnais et pas le modèle.**

---

## Avec quoi on le construit

Rien de tout cela n'est à écrire de zéro. L'outillage existe, il est libre, et il tient en trois briques plus une.

**Le socle est Inspect AI**, le cadre d'évaluation de l'institut britannique de sécurité de l'IA. C'est le seul outil sous licence MIT, très actif, qui couvre à la fois les questions-réponses classiques, la notation par grille avec plusieurs juges, et l'agentique en conteneur, avec des journaux exploitables. Il accepte nativement une **liste de modèles juges avec vote majoritaire**, ce qui règle la question du jury multi-familles en quelques lignes. Il sait aussi poser des limites dures en jetons, en messages et en temps, ce qui est exactement le levier pour serrer le budget d'erreur.

**YourBench** sert à fabriquer du volume sur les catégories documentaires. On lui donne un dossier de pièces réelles, il en tire des questions ancrées, chacune devant citer son passage source. Deux choses à savoir avant de s'y mettre : c'est en mode maintenance depuis fin 2025, sans nouveauté fonctionnelle depuis sept mois, et leur propre validation humaine donne environ **quinze pour cent d'items à jeter**. Donc générer, puis relire. En contrepartie, l'argument qui compte est solide : ils reproduisent des sous-ensembles de MMLU pour moins de quinze dollars en conservant parfaitement le classement des modèles. Le signal survit à la génération automatique.

**Harbor**, successeur de Terminal-Bench, prend tout ce qui a une vérification objective : un script qui doit produire le bon média, un fichier de montage qui doit être valide, un correctif qui doit compiler. Il fait tourner de vrais agents en ligne de commande dans des conteneurs. C'est le projet le plus vivant du domaine à ce jour.

La brique de plus, et c'est celle qu'on oublie toujours : **calibrer le jury avant de lui faire confiance**. Judgemark, développé dans la famille EQ-Bench, sert exactement à ça : il ne mesure pas les modèles, il mesure les **juges**, leur stabilité d'un tour à l'autre et leur capacité à séparer un bon texte d'un excellent. Un détail contre-intuitif y est documenté et mérite d'être retenu : leur mode « book club », où les juges débattent avant de noter, **dégrade** la qualité du jugement, les juges étant meilleurs avec le moins de distracteurs en contexte. Le jury doit voter, pas délibérer.

Ce que je n'utiliserais pas, et pour une raison de fond : les plateformes propriétaires d'observabilité. Un jeu d'épreuves privé dont l'intérêt est de ne jamais fuiter n'a rien à faire chez un tiers, quel que soit le confort de l'interface.

L'ordre de construction compte plus que l'outillage. **Le premier jour ne consiste pas à installer, il consiste à écrire cinquante épreuves à la main**, dix par catégorie, tirées de travail réel. Ce sont les seules dont on sait avec certitude ce qu'elles valent, et elles servent ensuite à juger tout ce que la génération automatique produira. Les rubriques viennent ensuite, la génération de volume après, les tâches agentiques après encore, et la calibration du jury en dernier avant de figer une version datée. Compter une vingtaine d'heures de travail effectif et quelques dizaines d'euros d'appels pour un premier cycle complet.

Une dernière règle, empruntée à un incident survenu sur tau-bench en juillet 2026 : une version figée ne se modifie jamais en place. Leur version 1.0.1 a corrigé la notation d'un domaine, rendant du même coup incomparables tous les résultats produits avec la version antérieure. Un banc d'essai dont on corrige la notation en cours de route produit des scores qui ne sont plus comparables entre eux, et on ne s'en aperçoit qu'après avoir tiré des conclusions.

---

## Ce que ça produit, et pourquoi ça vaut la peine

Un tableau à cinq colonnes de phases et cinq lignes de catégories, mis à jour à chaque nouveau modèle, qui répond à une seule question : qui j'appelle, pour quoi. C'est un instrument de routage, pas un palmarès.

Et un actif dérivé, plus intéressant que le tableau. Le champ manque cruellement d'une chose : des données structurées sur les **décisions** de création, le chemin plutôt que le résultat. Personne ne possède le corpus des raisons pour lesquelles une direction a été écartée. Un banc d'essai construit sur du travail réel, tenu dans la durée, fabrique mécaniquement ce corpus. C'est le seul actif de cette pratique qu'aucun laboratoire ne peut acheter, parce qu'il ne se collecte pas à l'échelle : il faut des années de travail d'une même personne pour qu'il ait un sens.

Reste la limite honnête, et elle est double. Un jeu privé n'est pas reproductible, donc ses résultats ne valent que pour celui qui l'a construit et ne prouvent rien publiquement. Et un juge unique sur les dimensions de goût, c'est un goût, pas une mesure. Je l'assume : ce n'est pas un instrument scientifique, c'est un instrument d'atelier. Sa validité est locale par construction, et c'est précisément ce qui le rend utile là où les instruments universels ne disent rien.

---

*Protocole, pas résultat. Il ne vaudra quelque chose qu'après avoir tourné deux fois sur des modèles réels.*
