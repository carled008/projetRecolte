# Équipe : The Pythonists

**Lien du tableau de bord :** (à coller ici une fois déployé sur Streamlit Community Cloud)

| Membre | Identifiant GitHub | Rôle principal |
|---|---|---|
| Ridore Carl-Edouard | carled008 | Analyses statistiques et graphiques (Questions 4, 5 et 6) |
| Louis Ansouby | LouisAnsouby | Analyses temporelles et territoriales (Questions 7 et 8, Synthèse) |
| Membre 4 | @github_id4 | Diagnostic initial, nettoyage des données et jointures |
| Faustin Raphael | kielelhueiie | Tableau de bord Streamlit (`app.py`) et mise en ligne |

## Qui a fait quoi

- **Ridore Carl-Edouard (@carled008)** : J'ai réalisé les analyses des questions 4, 5 et 6 (poids en volume vs valeur économique, rendements par département et influence de la pluviométrie avec nuages de points et tendances).
- **Louis Ansouby (@LouisAnsouby)** : J'ai réalisé les questions 7 et 8 (dynamique d'évolution des cultures entre 2023 et 2025, calcul de la production par habitant selon les départements) et rédigé la synthèse des résultats.
- **Membre 4 (@github_id4)** : Diagnostic du fichier brut (anomalies de types, valeurs manquantes, déduplication), nettoyage étape par étape jusqu'à la forme `(376, 6)`, jointures relationnelles et export de `donnees/recoltes_propre.csv`.
- **Faustin Raphael (@kielelhueiie)** : Conception et implémentation du tableau de bord Streamlit (`app.py`) en 6 étapes (chargement `@st.cache_data`, filtres dynamiques, indicateurs clés `st.metric`, 5 onglets `st.tabs`, conclusion, limites des données et export CSV), puis déploiement de l'application en ligne.
