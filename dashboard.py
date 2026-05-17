import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard BGES", layout="wide")

@st.cache_data
def load_data():
    faits_mission = pd.read_csv("TABLES/FAITS_MISSION.csv")
    faits_mat = pd.read_csv("TABLES/FAITS_MATERIEL_INFORMATIQUE.csv")
    mission = pd.read_csv("TABLES/MISSION.csv")
    materiel = pd.read_csv("TABLES/MATERIEL_INFORMATIQUE.csv")
    personnel = pd.read_csv("TABLES/PERSONNEL.csv")
    localisation = pd.read_csv("TABLES/LOCALISATION.csv")
    return faits_mission, faits_mat, mission, materiel, personnel, localisation

FAITS_MISSION, FAITS_MATERIEL, MISSION, MATERIEL, PERSONNEL, LOCALISATION = load_data()

missions = (
    FAITS_MISSION
    .merge(MISSION, on="ID_MISSION", how="left")
    .merge(PERSONNEL, on="ID_PERSONNEL", how="left")
)

materiels = (
    FAITS_MATERIEL
    .merge(MATERIEL, on="ID_MATERIELINFO", how="left")
    .merge(PERSONNEL, on="ID_PERSONNEL", how="left")
)

st.title("Dashboard BGES - Missions et Matériel informatique")

sites = sorted(set(missions["SITE"].dropna()).union(set(materiels["SITE"].dropna())))
selected_sites = st.sidebar.multiselect("Sites", sites, default=sites)

mois = st.sidebar.slider("Mois", 4, 11, (4, 11))

fonctions = sorted(PERSONNEL["FONCTION_PERSONNEL"].dropna().unique())
selected_fonctions = st.sidebar.multiselect("Secteurs d'activité", fonctions, default=fonctions)

missions_f = missions[
    missions["SITE"].isin(selected_sites)
    & missions["MOIS"].between(mois[0], mois[1])
    & missions["FONCTION_PERSONNEL"].isin(selected_fonctions)
]

materiels_f = materiels[
    materiels["SITE"].isin(selected_sites)
    & materiels["MOIS"].between(mois[0], mois[1])
    & materiels["FONCTION_PERSONNEL"].isin(selected_fonctions)
]

impact_missions = missions_f["IMPACT_CARBONE"].sum()
impact_materiel = materiels_f["IMPACT"].sum()
impact_total = impact_missions + impact_materiel

c1, c2, c3 = st.columns(3)
c1.metric("Impact missions", f"{impact_missions:.2f} tCO₂e")
c2.metric("Impact matériel", f"{impact_materiel:.2f} tCO₂e")
c3.metric("Impact total", f"{impact_total:.2f} tCO₂e")

st.divider()
st.header("Figures décisionnelles")

st.subheader("Top 5 des missions les plus impactantes sur le site de Paris")

result18 = (
    missions[missions["SITE"] == "Paris"]
    .groupby(["ID_MISSION", "TYPE_MISSION"], as_index=False)["IMPACT_CARBONE"]
    .sum()
    .rename(columns={"IMPACT_CARBONE": "IMPACT_TOTAL"})
    .sort_values("IMPACT_TOTAL", ascending=False)
    .head(5)
)

fig18 = px.bar(
    result18,
    x="ID_MISSION",
    y="IMPACT_TOTAL",
    color="TYPE_MISSION",
    title="Top 5 des missions les plus impactantes à Paris",
    labels={
        "ID_MISSION": "Mission",
        "IMPACT_TOTAL": "Impact carbone (tCO₂e)",
        "TYPE_MISSION": "Type de mission"
    }
)

st.plotly_chart(fig18, use_container_width=True)

st.subheader("Impact mensuel des missions par transport et par site")

result19 = (
    missions
    .groupby(["SITE", "MOIS", "TRANSPORT"], as_index=False)["IMPACT_CARBONE"]
    .sum()
    .rename(columns={"IMPACT_CARBONE": "IMPACT_TOTAL"})
)

result19["PERIODE"] = "2026-" + result19["MOIS"].astype(str).str.zfill(2)

fig19 = px.bar(
    result19,
    x="PERIODE",
    y="IMPACT_TOTAL",
    color="TRANSPORT",
    facet_col="SITE",
    facet_col_wrap=3,
    title="Impact carbone mensuel des missions par transport et par site",
    labels={
        "PERIODE": "Mois",
        "IMPACT_TOTAL": "Impact carbone (tCO₂e)",
        "TRANSPORT": "Transport"
    }
)

st.plotly_chart(fig19, use_container_width=True)

st.subheader("Impact carbone global mensuel de l'organisation")

impact_missions = (
    missions
    .groupby(["ANNEE", "MOIS"], as_index=False)["IMPACT_CARBONE"]
    .sum()
)

impact_materiel = (
    materiels
    .groupby(["ANNEE", "MOIS"], as_index=False)["IMPACT"]
    .sum()
)

result20 = impact_missions.merge(
    impact_materiel,
    on=["ANNEE", "MOIS"],
    how="outer"
).fillna(0)

result20["IMPACT_TOTAL"] = result20["IMPACT_CARBONE"] + result20["IMPACT"]

result20["PERIODE"] = (
    result20["ANNEE"].astype(str)
    + "-"
    + result20["MOIS"].astype(str).str.zfill(2)
)

result20 = result20.sort_values("PERIODE")

fig20 = px.line(
    result20,
    x="PERIODE",
    y="IMPACT_TOTAL",
    markers=True,
    title="Impact carbone global mensuel",
    labels={
        "PERIODE": "Mois",
        "IMPACT_TOTAL": "Impact carbone total (tCO₂e)"
    }
)

st.plotly_chart(fig20, use_container_width=True)

st.divider()
st.header("Questions décisionnelles")

question = st.selectbox(
    "Choisir une question",
    [
        "10. Secteur le plus impactant",
        "11. Site le plus impactant",
        "12. Missions entre sites en septembre 2026",
        "13. Impact des séminaires à Los Angeles en juillet 2026",
        "14. Secteur le plus impactant pour les conférences",
        "15. Âge moyen des Data Engineers en formation",
        "16. Destination la plus impactante",
        "17. Top 3 catégories de missions pour les cadres en Europe"
    ]
)

if question == "10. Secteur le plus impactant":
    impact_missions_q = missions.groupby("FONCTION_PERSONNEL", as_index=False)["IMPACT_CARBONE"].sum()
    impact_materiel_q = materiels.groupby("FONCTION_PERSONNEL", as_index=False)["IMPACT"].sum()

    result = impact_missions_q.merge(
        impact_materiel_q,
        on="FONCTION_PERSONNEL",
        how="outer"
    ).fillna(0)

    result["IMPACT_TOTAL"] = result["IMPACT_CARBONE"] + result["IMPACT"]
    result = result.sort_values("IMPACT_TOTAL", ascending=False)

    st.dataframe(result, use_container_width=True)

elif question == "11. Site le plus impactant":
    impact_missions_q = missions.groupby("SITE", as_index=False)["IMPACT_CARBONE"].sum()
    impact_materiel_q = materiels.groupby("SITE", as_index=False)["IMPACT"].sum()

    result = impact_missions_q.merge(
        impact_materiel_q,
        on="SITE",
        how="outer"
    ).fillna(0)

    result["IMPACT_TOTAL"] = result["IMPACT_CARBONE"] + result["IMPACT"]
    result = result.sort_values("IMPACT_TOTAL", ascending=False)

    st.dataframe(result, use_container_width=True)

elif question == "12. Missions entre sites en septembre 2026":
    sites_org = set(sites)

    result = missions[
        (missions["ANNEE"] == 2026)
        & (missions["MOIS"] == 9)
        & (missions["VILLE_DEPART"].isin(sites_org))
        & (missions["VILLE_DESTINATION"].isin(sites_org))
    ]

    result = result.groupby(
        ["VILLE_DEPART", "VILLE_DESTINATION"],
        as_index=False
    )["IMPACT_CARBONE"].sum()

    result = result.rename(columns={"IMPACT_CARBONE": "IMPACT_TOTAL"})
    result = result.sort_values("IMPACT_TOTAL", ascending=False)

    st.dataframe(result, use_container_width=True)

elif question == "13. Impact des séminaires à Los Angeles en juillet 2026":
    result = missions[
        (missions["ANNEE"] == 2026)
        & (missions["MOIS"] == 7)
        & (missions["SITE"] == "Los Angeles")
        & (missions["TYPE_MISSION"].isin(["Seminar", "Séminaire", "Seminaire"]))
    ]

    impact = result["IMPACT_CARBONE"].sum()
    st.metric("Impact total", f"{impact:.2f} tCO₂e")

elif question == "14. Secteur le plus impactant pour les conférences":
    result = missions[
        (missions["ANNEE"] == 2026)
        & (missions["MOIS"].between(5, 9))
        & (missions["TYPE_MISSION"] == "Conference")
    ]

    result = result.groupby(
        "FONCTION_PERSONNEL",
        as_index=False
    )["IMPACT_CARBONE"].sum()

    result = result.sort_values("IMPACT_CARBONE", ascending=False)

    st.dataframe(result, use_container_width=True)

elif question == "15. Âge moyen des Data Engineers en formation":
    result = missions[
        (missions["ANNEE"] == 2026)
        & (missions["MOIS"].between(7, 9))
        & (missions["TYPE_MISSION"] == "Training")
        & (missions["FONCTION_PERSONNEL"] == "Data Engineer")
    ].copy()

    result["DATE_NAISSANCE"] = pd.to_datetime(result["DATE_NAISSANCE"], errors="coerce")
    result["AGE"] = (pd.Timestamp.today() - result["DATE_NAISSANCE"]).dt.days / 365.25

    st.metric("Âge moyen", f"{result['AGE'].mean():.1f} ans")

elif question == "16. Destination la plus impactante":
    result = missions[
        (missions["ANNEE"] == 2026)
        & (missions["MOIS"].between(5, 10))
    ]

    result = result.groupby(
        "VILLE_DESTINATION",
        as_index=False
    )["IMPACT_CARBONE"].sum()

    result = result.sort_values("IMPACT_CARBONE", ascending=False)

    st.dataframe(result, use_container_width=True)

elif question == "17. Top 3 catégories de missions pour les cadres en Europe":
    missions_loc = missions.merge(
        LOCALISATION,
        left_on="VILLE_DESTINATION",
        right_on="VILLE",
        how="left"
    )

    result = missions_loc[
        (missions_loc["ANNEE"] == 2026)
        & (missions_loc["MOIS"] == 5)
        & (missions_loc["FONCTION_PERSONNEL"] == "Manager")
        & (missions_loc["CONTINENT"] == "Europe")
    ]

    result = result.groupby(
        "TYPE_MISSION",
        as_index=False
    )["IMPACT_CARBONE"].sum()

    result = result.sort_values("IMPACT_CARBONE", ascending=False).head(3)

    st.dataframe(result, use_container_width=True)