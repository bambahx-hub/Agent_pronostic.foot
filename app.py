import streamlit as st
import pandas as pd
from io import StringIO
from datetime import datetime

st.set_page_config(page_title="Pronostics Football — Betclic uniquement", page_icon="⚽", layout="wide")

st.title("⚽ Tableau de bord — Matchs Betclic uniquement")
st.caption("Version 2 · Import manuel de données Betclic · Aucun pari automatique")

st.warning(
    "Ce tableau de bord n'est pas connecté à Betclic. Il n'affiche que les matchs que vous importez "
    "depuis Betclic. Les données importées ne sont pas vérifiées automatiquement. N'ajoutez pas votre "
    "mot de passe, code SMS ou informations Mobile Money."
)

REQUIRED = ["date", "heure", "competition", "domicile", "exterieur"]
OPTIONAL = ["cote_1", "cote_n", "cote_2", "source"]

SAMPLE_CSV = """date,heure,competition,domicile,exterieur,cote_1,cote_n,cote_2,source
2026-10-28,18:00,Exemple à remplacer,Équipe domicile,Équipe extérieure,2.10,3.20,3.40,Betclic
"""

def normalize(df):
    df = df.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]
    aliases = {
        "date du match": "date", "kickoff": "heure", "time": "heure",
        "ligue": "competition", "championnat": "competition",
        "équipe domicile": "domicile", "equipe domicile": "domicile",
        "home": "domicile", "équipe extérieure": "exterieur",
        "equipe extérieure": "exterieur", "away": "exterieur",
        "1": "cote_1", "cote 1": "cote_1", "cote domicile": "cote_1",
        "n": "cote_n", "cote n": "cote_n", "nul": "cote_n",
        "2": "cote_2", "cote 2": "cote_2", "cote extérieur": "cote_2",
        "equipe exterieure": "exterieur", "cote exterieur": "cote_2",
    }
    df = df.rename(columns={c: aliases.get(c, c) for c in df.columns})
    return df

def implied(row):
    odds = []
    for c in ["cote_1", "cote_n", "cote_2"]:
        try:
            x = float(row.get(c))
            odds.append(1/x if x > 1 else None)
        except (TypeError, ValueError):
            odds.append(None)
    valid = [x for x in odds if x is not None]
    if not valid:
        return (None, None, None)
    total = sum(valid)
    return tuple(round(x / total * 100, 1) if x is not None else None for x in odds)

uploaded = st.file_uploader("Importer un fichier CSV exporté/préparé à partir des matchs Betclic", type=["csv"])
with st.expander("Comment préparer le fichier ?"):
    st.markdown(
        "- Copiez uniquement les rencontres visibles sur Betclic Côte d’Ivoire dans un fichier CSV.\n"
        "- Colonnes obligatoires : `date`, `heure`, `competition`, `domicile`, `exterieur`.\n"
        "- Colonnes facultatives pour les cotes : `cote_1` (victoire domicile), `cote_n` (nul), `cote_2` (victoire extérieur), `source`.\n"
        "- Vous pouvez télécharger le modèle ci-dessous. Remplacez les lignes d’exemple par les vraies rencontres Betclic.\n"
        "- Le tableau n’invente pas de matchs : sans import, la liste reste vide."
    )
    st.download_button("Télécharger le modèle CSV", SAMPLE_CSV, "modele_matchs_betclic.csv", "text/csv")

if uploaded is not None:
    try:
        raw = pd.read_csv(uploaded)
        df = normalize(raw)
        missing = [c for c in REQUIRED if c not in df.columns]
        if missing:
            st.error("Colonnes obligatoires manquantes : " + ", ".join(missing))
            st.caption("Utilisez le modèle CSV et gardez les noms de colonnes indiqués.")
            df = pd.DataFrame(columns=REQUIRED + OPTIONAL)
        else:
            for c in OPTIONAL:
                if c not in df.columns:
                    df[c] = None
            df = df[REQUIRED + OPTIONAL].dropna(subset=["domicile", "exterieur"])
            df = df[(df["domicile"].astype(str).str.strip() != "") & (df["exterieur"].astype(str).str.strip() != "")]
            df["source"] = df["source"].fillna("Import utilisateur — Betclic déclaré")
            st.success(f"{len(df)} match(s) importé(s). Vérifiez qu'ils apparaissent bien sur Betclic Côte d’Ivoire.")
    except Exception as e:
        st.error(f"Impossible de lire le CSV : {e}")
        df = pd.DataFrame(columns=REQUIRED + OPTIONAL)
else:
    df = pd.DataFrame(columns=REQUIRED + OPTIONAL)

st.subheader("Rencontres importées")
if df.empty:
    st.info("Aucun match affiché pour le moment. Importez un CSV contenant uniquement les matchs Betclic que vous voyez.")
else:
    df = df.copy()
    probs = df.apply(implied, axis=1, result_type="expand")
    probs.columns = ["P(1) %", "P(N) %", "P(2) %"]
    view = pd.concat([df.reset_index(drop=True), probs], axis=1)
    st.dataframe(view, use_container_width=True, hide_index=True)
    st.caption("Les probabilités affichées sont déduites des cotes importées et normalisées. Ce ne sont pas des prédictions garanties.")

    st.subheader("Analyse d’un match")
    choices = [f"{r['domicile']} — {r['exterieur']}" for _, r in df.iterrows()]
    idx = st.selectbox("Choisir une rencontre", range(len(choices)), format_func=lambda i: choices[i])
    r = df.iloc[idx]
    c1, c2, c3 = st.columns(3)
    for col, key, label in [(c1, "cote_1", "Victoire domicile (1)"), (c2, "cote_n", "Match nul (N)"), (c3, "cote_2", "Victoire extérieur (2)")]:
        try:
            val = float(r[key])
            col.metric(label, f"{val:.2f}" if val > 1 else "Cote absente")
        except (TypeError, ValueError):
            col.metric(label, "Cote absente")
    st.write(f"**Compétition :** {r['competition']}  ·  **Date :** {r['date']}  ·  **Heure :** {r['heure']}")
    st.write("**Source déclarée :** " + str(r["source"]))
    st.info("Ce prototype ne collecte pas les statistiques d’équipes et ne peut pas confirmer les cotes en direct. Utilisez-le comme outil de lecture, pas comme garantie de gain.")

st.divider()
st.subheader("Limites et sécurité")
st.markdown(
    "- Pas de connexion à votre compte Betclic, pas de collecte automatique, pas de mise ni de coupon envoyé automatiquement.\n"
    "- N'entrez jamais vos identifiants ou codes de validation dans ce tableau de bord.\n"
    "- Pour une collecte automatique, il faut d’abord un moyen officiel et autorisé d’accéder aux matchs et cotes Betclic.\n"
    "- Les paris comportent un risque de perte. Une cote et une probabilité implicite ne garantissent aucun résultat."
)
