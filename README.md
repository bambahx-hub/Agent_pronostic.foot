# Tableau de bord Pronostics Football — Betclic uniquement (V2)

## Ce que fait cette version
- Affiche uniquement les rencontres importées dans un fichier CSV par l'utilisateur.
- Permet d'importer dates, équipes, compétition et cotes 1/N/2.
- Calcule des probabilités implicites normalisées à partir des cotes fournies.
- Ne crée pas de matchs fictifs dans le tableau de bord et n'envoie aucun pari.

## Ce qu'elle ne fait pas
- Elle n'est pas connectée à Betclic Côte d'Ivoire.
- Elle ne vérifie pas automatiquement que les rencontres/cotes sont encore présentes sur Betclic.
- Elle ne prédit pas de manière fiable les gagnants et ne garantit aucun gain.
- Elle ne place aucun pari.

## Démarrage sur un ordinateur
1. Installer Python 3.10 ou plus récent.
2. Ouvrir un terminal dans le dossier du projet.
3. Installer les dépendances :
   `pip install -r requirements.txt`
4. Lancer :
   `streamlit run app.py`
5. Ouvrir l'adresse locale affichée par Streamlit.

## Format CSV
Colonnes obligatoires :
`date,heure,competition,domicile,exterieur`

Colonnes facultatives :
`cote_1,cote_n,cote_2,source`

Exemple de ligne (à remplacer par un vrai match Betclic) :
`2026-10-28,18:00,Ligue Exemple,Équipe A,Équipe B,2.10,3.20,3.40,Betclic`

## Hébergement permanent
Pour que le tableau de bord reste disponible quand le téléphone est éteint ou hors ligne, il faut l'héberger sur un serveur. Cette archive ne crée pas à elle seule un compte d'hébergement et ne publie pas le site automatiquement. Un service d'hébergement peut exiger une inscription et une action de validation par son propriétaire.

## Sécurité
Ne mettez jamais un mot de passe Betclic, code SMS, PIN ou identifiant Mobile Money dans un CSV ou dans l'application.
