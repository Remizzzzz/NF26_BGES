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
st.header("Figures interactives")

st.subheader("18. Top missions les plus impactantes par site")

col_a, col_b = st.columns(2)

with col_a:
    site_q18 = st.selectbox(
        "Site à analyser",
        sorted(missions["SITE"].dropna().unique()),
        index=sorted(missions["SITE"].dropna().unique()).index("Paris")
        if "Paris" in sorted(missions["SITE"].dropna().unique()) else 0
    )

with col_b:
    top_n_q18 = st.slider("Nombre de missions à afficher", 3, 15, 5)

result18 = (
    missions[missions["SITE"] == site_q18]
    .groupby(["ID_MISSION", "TYPE_MISSION"], as_index=False)["IMPACT_CARBONE"]
    .sum()
    .rename(columns={"IMPACT_CARBONE": "IMPACT_TOTAL"})
    .sort_values("IMPACT_TOTAL", ascending=False)
    .head(top_n_q18)
)

fig18 = px.bar(
    result18,
    x="ID_MISSION",
    y="IMPACT_TOTAL",
    color="TYPE_MISSION",
    title=f"Top {top_n_q18} des missions les plus impactantes - {site_q18}",
    labels={
        "ID_MISSION": "Mission",
        "IMPACT_TOTAL": "Impact carbone (tCO₂e)",
        "TYPE_MISSION": "Type de mission"
    },
    text="IMPACT_TOTAL"
)

fig18.update_traces(texttemplate="%{text:.2f}", textposition="outside")
fig18.update_layout(xaxis_tickangle=-45)

st.plotly_chart(fig18, use_container_width=True)


st.subheader("19. Impact mensuel des missions par transport et par site")

col_a, col_b, col_c = st.columns(3)

with col_a:
    sites_q19 = st.multiselect(
        "Sites affichés",
        sorted(missions["SITE"].dropna().unique()),
        default=sorted(missions["SITE"].dropna().unique())
    )

with col_b:
    transports_q19 = st.multiselect(
        "Transports affichés",
        sorted(missions["TRANSPORT"].dropna().unique()),
        default=sorted(missions["TRANSPORT"].dropna().unique())
    )

with col_c:
    type_graph_q19 = st.selectbox(
        "Type de graphique",
        ["Barres empilées", "Courbes"]
    )

result19 = missions[
    missions["SITE"].isin(sites_q19)
    & missions["TRANSPORT"].isin(transports_q19)
    & missions["MOIS"].between(mois[0], mois[1])
]

result19 = (
    result19
    .groupby(["SITE", "MOIS", "TRANSPORT"], as_index=False)["IMPACT_CARBONE"]
    .sum()
    .rename(columns={"IMPACT_CARBONE": "IMPACT_TOTAL"})
)

result19["PERIODE"] = "2026-" + result19["MOIS"].astype(str).str.zfill(2)

if type_graph_q19 == "Barres empilées":
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
else:
    fig19 = px.line(
        result19,
        x="PERIODE",
        y="IMPACT_TOTAL",
        color="TRANSPORT",
        facet_col="SITE",
        facet_col_wrap=3,
        markers=True,
        title="Impact carbone mensuel des missions par transport et par site",
        labels={
            "PERIODE": "Mois",
            "IMPACT_TOTAL": "Impact carbone (tCO₂e)",
            "TRANSPORT": "Transport"
        }
    )

st.plotly_chart(fig19, use_container_width=True)


st.subheader("20. Impact carbone global mensuel de l'organisation")

col_a, col_b = st.columns(2)

with col_a:
    sources_q20 = st.multiselect(
        "Sources d'impact",
        ["Missions", "Matériel"],
        default=["Missions", "Matériel"]
    )

with col_b:
    affichage_q20 = st.selectbox(
        "Affichage",
        ["Impact total", "Détail missions / matériel"]
    )

impact_missions_20 = (
    missions_f
    .groupby(["ANNEE", "MOIS"], as_index=False)["IMPACT_CARBONE"]
    .sum()
)

impact_materiel_20 = (
    materiels_f
    .groupby(["ANNEE", "MOIS"], as_index=False)["IMPACT"]
    .sum()
)

result20 = impact_missions_20.merge(
    impact_materiel_20,
    on=["ANNEE", "MOIS"],
    how="outer"
).fillna(0)

if "Missions" not in sources_q20:
    result20["IMPACT_CARBONE"] = 0

if "Matériel" not in sources_q20:
    result20["IMPACT"] = 0

result20["IMPACT_TOTAL"] = result20["IMPACT_CARBONE"] + result20["IMPACT"]

result20["PERIODE"] = (
    result20["ANNEE"].astype(str)
    + "-"
    + result20["MOIS"].astype(str).str.zfill(2)
)

result20 = result20.sort_values("PERIODE")

if affichage_q20 == "Impact total":
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
else:
    value_vars = []

    if "Missions" in sources_q20:
        value_vars.append("IMPACT_CARBONE")

    if "Matériel" in sources_q20:
        value_vars.append("IMPACT")

    if len(value_vars) == 0:
        st.warning("Sélectionne au moins une source d'impact.")
    else:
        result20_long = result20.melt(
            id_vars=["PERIODE"],
            value_vars=value_vars,
            var_name="SOURCE",
            value_name="VALEUR_IMPACT"
        )

        result20_long["SOURCE"] = result20_long["SOURCE"].replace({
            "IMPACT_CARBONE": "Missions",
            "IMPACT": "Matériel"
        })

        fig20 = px.bar(
            result20_long,
            x="PERIODE",
            y="VALEUR_IMPACT",
            color="SOURCE",
            barmode="stack",
            title="Impact carbone mensuel détaillé missions / matériel",
            labels={
                "PERIODE": "Mois",
                "VALEUR_IMPACT": "Impact carbone (tCO₂e)",
                "SOURCE": "Source"
            }
        )

        st.plotly_chart(fig20, use_container_width=True)

st.dataframe(result20, use_container_width=True)

st.divider()
st.header("Questions")

question = st.selectbox(
    "Choisir une question",
    [
        "10. Secteur le plus impactant",
        "11. Site le plus impactant",
        "12. Impact carbone entre sites de l'organisation",
        "13. Impact des formations à Los Angeles",
        "14. Secteur le plus impactant pour les conférences",
        "15. Âge moyen des Data Engineers en formation",
        "16. Destination la plus impactante",
        "17. Top 3 catégories de missions pour les Managers en Europe"
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

elif question == "12. Impact carbone entre sites de l'organisation":
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

    fig = px.bar(
        result,
        x="VILLE_DEPART",
        y="IMPACT_TOTAL",
        color="VILLE_DESTINATION",
        title="Impact carbone entre les sites en septembre 2026",
        labels={
            "VILLE_DEPART": "Site de départ",
            "VILLE_DESTINATION": "Site destination",
            "IMPACT_TOTAL": "Impact carbone (tCO₂e)"
        }
    )

    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(result, use_container_width=True)


elif question == "13. Impact des formations à Los Angeles":
    result = missions[
        (missions["ANNEE"] == 2026)
        & (missions["MOIS"] == 7)
        & (missions["SITE"] == "Los Angeles")
        & (missions["TYPE_MISSION"] == "Training")
    ]

    impact = result["IMPACT_CARBONE"].sum()

    st.metric("Impact total", f"{impact:.2f} tCO₂e")

    st.dataframe(
        result[
            [
                "ID_MISSION",
                "TYPE_MISSION",
                "TRANSPORT",
                "VILLE_DESTINATION",
                "IMPACT_CARBONE"
            ]
        ],
        use_container_width=True
    )


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

    fig = px.bar(
        result,
        x="FONCTION_PERSONNEL",
        y="IMPACT_CARBONE",
        color="FONCTION_PERSONNEL",
        title="Impact carbone des conférences par secteur",
        labels={
            "FONCTION_PERSONNEL": "Secteur",
            "IMPACT_CARBONE": "Impact carbone (tCO₂e)"
        }
    )

    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(result, use_container_width=True)


elif question == "15. Âge moyen des Data Engineers en formation":
    result = missions[
        (missions["ANNEE"] == 2026)
        & (missions["MOIS"].between(7, 9))
        & (missions["TYPE_MISSION"] == "Training")
        & (missions["FONCTION_PERSONNEL"] == "Data Engineer")
    ].copy()

    result["DATE_NAISSANCE"] = pd.to_datetime(
        result["DATE_NAISSANCE"],
        errors="coerce"
    )

    result["AGE"] = (
        pd.Timestamp("2026-09-01") - result["DATE_NAISSANCE"]
    ).dt.days / 365.25

    st.metric("Âge moyen", f"{result['AGE'].mean():.1f} ans")

    fig = px.histogram(
        result,
        x="AGE",
        nbins=10,
        title="Répartition des âges des Data Engineers en formation"
    )

    st.plotly_chart(fig, use_container_width=True)


elif question == "16. Destination la plus impactante":
    result = missions[
        (missions["ANNEE"] == 2026)
        & (missions["MOIS"].between(5, 10))
    ]

    result = result.groupby(
        "VILLE_DESTINATION",
        as_index=False
    )["IMPACT_CARBONE"].sum()

    result = result.sort_values(
        "IMPACT_CARBONE",
        ascending=False
    )

    fig = px.bar(
        result.head(10),
        x="VILLE_DESTINATION",
        y="IMPACT_CARBONE",
        color="VILLE_DESTINATION",
        title="Destinations les plus impactantes",
        labels={
            "VILLE_DESTINATION": "Destination",
            "IMPACT_CARBONE": "Impact carbone (tCO₂e)"
        }
    )

    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(result, use_container_width=True)


elif question == "17. Top 3 catégories de missions pour les Managers en Europe":
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

    result = result.sort_values(
        "IMPACT_CARBONE",
        ascending=False
    ).head(3)

    fig = px.pie(
        result,
        values="IMPACT_CARBONE",
        names="TYPE_MISSION",
        title="Top 3 des catégories de missions pour les Managers en Europe"
    )

    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(result, use_container_width=True)