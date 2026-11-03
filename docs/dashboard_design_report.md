# Dashboard de recherche de stage — note de conception

## Objectif et périmètre

Le dashboard transforme `docs/data/matches.json` en vue de décision : où le pipeline a-t-il des données, quelles offres couvrent le profil, et quelles compétences méritent une action ? Il distingue les indicateurs calculables des informations qui ne sont pas encore collectées. Le tableau de bord est alimenté directement par le fichier JSON publié et ne dépend d’aucune bibliothèque externe.

Les catégories ci-dessous reprennent le brief indiqué dans la consigne. Les fichiers `project1_internship_job_search.md` et `TD_5_STUDENT_MANUAL_dashboard_design.md` n’étant pas présents dans ce dépôt, cette note s’appuie sur les critères décrits dans la demande.

## Lecture des données actuelles

Le dernier `matches.json` contient 50 offres France Travail publiables. Les scores de couverture ont 20 offres à 0 %, 28 entre 1 et 49 %, une entre 50 et 79 %, et une à 100 %. La couverture moyenne est donc de 24,4 %; 30 offres ont au moins une compétence correspondante. AWS est la lacune la plus fréquente (10 offres), suivi de Terraform (8), puis Linux et PyTorch (6 chacun). Python est le point fort le plus souvent demandé : 28 offres, niveau autoévalué 4/5.

Huit offres sur 50 mentionnent une rémunération explicite (16 %). Ce champ reste un indicateur de disponibilité de l’information, pas de niveau de rémunération : les montants et périodes n’ont pas été normalisés dans les données fournies.

## KPI et décisions

| Catégorie | KPI affiché | Définition | Décision soutenue |
|---|---|---|---|
| Santé du pipeline | Offres par source | Nombre d’offres groupées par `source` | Voir quelles sources alimentent le pipeline et si une source est absente. La vue signale qu’il n’y a actuellement qu’une source. |
| Santé du pipeline | Complétude des compétences extraites | Part des offres ayant une liste `required_skills` non vide | Repérer un lot à retraiter si l’extraction de compétences ne produit plus de critères. Ce KPI est un contrôle de complétude, pas un taux d’erreur sémantique. |
| Efficacité de recherche | Couverture moyenne et répartition des scores | Moyenne de `coverage` (ou `score`) et nombre d’offres par tranche | Choisir les offres à examiner en premier et voir si la recherche trouve des postes plausibles pour le profil. |
| Efficacité de recherche | Fréquence des lacunes et compétences correspondantes | Agrégats `top_skill_gaps` et `top_matched_skills` | Prioriser l’apprentissage et repérer les forces à mettre en avant dans les candidatures. |
| Résultats | Candidatures, réponses et entretiens | Non calculés : absents de `matches.json` | Le dashboard rend visible le besoin d’un journal de candidatures avant d’interpréter l’efficacité en résultats réels. |
| Qualité d’extraction | Taux d’erreur de critique | Non calculé : aucune annotation de critique indépendante n’est fournie | Éviter de confondre « champ rempli » et « contenu correct ». Instrumenter un échantillon vérifié à la main pour mesurer les erreurs. |

Le niveau de rémunération cité est un KPI complémentaire intéressant : il reflète la transparence des offres et peut aider à repérer où le candidat devra demander des précisions. Il est affiché en nombre et en proportion, sans inventer de montants absents.

## Pourquoi ces graphiques ?

| Visuel | Pour qui ? | Décision appuyée | Pourquoi ce type de graphique ? |
|---|---|---|---|
| Barres horizontales « offres par source » | La personne qui suit la collecte | Vérifier quelles sources apportent les offres et repérer une source manquante ou disproportionnée | Les barres permettent de comparer des catégories nommées et restent lisibles quand le nombre de sources augmente. Un camembert serait moins précis pour comparer de petits écarts; avec une seule source, le tableau de bord indique aussi clairement que la comparaison est impossible pour l’instant. |
| Histogramme à tranches de couverture | Le candidat qui sélectionne les annonces | Arbitrer entre candidatures très alignées, candidatures ambitieuses et offres sans correspondance détectée | Les tranches ordonnées montrent la distribution et la concentration des scores. Une moyenne seule masquerait les 20 offres à zéro; un camembert rendrait la progression des classes moins évidente. Les tranches sont explicites, y compris la classe zéro. |
| Barres de fréquence des lacunes | Le candidat qui planifie sa montée en compétences | Choisir les lacunes transversales à travailler en premier | Les barres ordonnées rendent visibles les rangs et l’écart de fréquence. Un nuage de mots donnerait moins de précision et n’aiderait pas à prioriser. Le décompte signifie « nombre d’offres qui citent cette lacune », pas gravité ni temps d’apprentissage. |
| Barres de compétences correspondantes, avec niveau | Le candidat qui prépare son CV et ses entretiens | Mettre en avant les compétences déjà demandées et calibrer les exemples à apporter | Même échelle et même forme que les lacunes : comparaison immédiate entre fréquence des besoins et acquis. Le niveau autoévalué est affiché à côté du nom, car la fréquence seule ne renseigne pas sur la maîtrise. |
| Tableau filtrable des offres | Le candidat au moment de décider de postuler | Comparer une offre précise, son score et les lacunes associées | Un tableau préserve les détails propres à chaque annonce et permet de rechercher par titre, entreprise ou lieu. Un graphique agrégé ne permettrait pas d’inspecter les offres individuelles. Le filtre par score réduit le temps de repérage. |

Les cartes KPI en tête donnent une lecture rapide, mais restent des nombres et proportions plutôt que des graphiques supplémentaires. Les réponses et le taux d’extraction erronée sont explicitement marqués « à instrumenter » : ils ne peuvent pas être déduits de ce fichier.

## Limites et prochaine mesure à ajouter

`score` est la proportion des compétences extraites retrouvées dans le profil. Il ne mesure ni la qualité globale d’une offre, ni sa compatibilité de localisation, d’expérience ou de rémunération. Une offre à 0 % peut aussi refléter un vocabulaire différent ou une extraction incomplète. Le chiffre de complétude ne contrôle pas si les compétences extraites sont vraies ou pertinentes.

Pour le taux d’erreur de critique, consigner pour chaque annonce auditée le nombre d’éléments extraits incorrects et le nombre d’éléments contrôlés, avec une définition stable de l’erreur. Pour les résultats, ajouter un fichier de suivi avec l’identifiant d’offre, la date d’envoi, le statut, la date de réponse et le type de réponse. On pourra alors calculer le taux de réponse comme offres ayant reçu une réponse ÷ candidatures envoyées, en précisant la fenêtre d’observation.
