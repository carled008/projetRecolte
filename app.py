from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="Tableau de bord : Les récoltes agricoles",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

DOSSIER = Path(__file__).parent / "donnees"


# ---------------------------------------------------------
# Étape 2 : Chargement des données avec @st.cache_data
# ---------------------------------------------------------
@st.cache_data
def charger_donnees():
    fichier = DOSSIER / "recoltes_propre.csv"
    if not fichier.exists():
        st.error(
            f"Fichier introuvable : {fichier}. "
            "Veuillez exécuter le notebook exploration.ipynb pour générer les données nettoyées."
        )
        st.stop()
    df = pd.read_csv(fichier)
    return df


df = charger_donnees()

# ---------------------------------------------------------
# Contexte et source
# ---------------------------------------------------------
st.title("🌾 Analyse des récoltes agricoles en Haïti (2023–2025)")
st.markdown(
    """
    Cette application présente l'analyse triennale des récoltes agricoles par département, saison et culture, 
    confiée par la Direction Départementale de l'Agriculture pour éclairer les décisions stratégiques du Ministère. 
    Elle met en lumière les volumes produits, leur valorisation économique, l'efficacité des rendements ainsi que l'impact des précipitations.
    
    **Source des données :** *Direction Départementale de l'Agriculture (données fictives - ESIH 2026).*
    """
)

# ---------------------------------------------------------
# Étape 3 : Filtres dans la barre latérale
# ---------------------------------------------------------
st.sidebar.header("🔍 Filtres d'analyse")

# Filtre Années
toutes_annees = sorted(df["annee"].unique().tolist())
annees_selectionnees = st.sidebar.multiselect(
    "Année(s) :",
    options=toutes_annees,
    default=toutes_annees,
)

# Filtre Saisons
toutes_saisons = sorted(df["saison"].unique().tolist())
saisons_selectionnees = st.sidebar.multiselect(
    "Saison(s) :",
    options=toutes_saisons,
    default=toutes_saisons,
)

# Filtre Départements
tous_departements = sorted(df["departement"].unique().tolist())
departements_selectionnes = st.sidebar.multiselect(
    "Département(s) :",
    options=tous_departements,
    default=tous_departements,
)

# Filtre Cultures
toutes_cultures = sorted(df["culture"].unique().tolist())
cultures_selectionnees = st.sidebar.multiselect(
    "Culture(s) :",
    options=toutes_cultures,
    default=toutes_cultures,
)

# Application des filtres
filtre = (
    df["annee"].isin(annees_selectionnees)
    & df["saison"].isin(saisons_selectionnees)
    & df["departement"].isin(departements_selectionnes)
    & df["culture"].isin(cultures_selectionnees)
)
df_filtre = df[filtre]

if df_filtre.empty:
    st.warning("⚠️ Aucune donnée ne correspond aux filtres sélectionnés. Veuillez ajuster votre sélection.")
    st.stop()

# ---------------------------------------------------------
# Étape 4 : Indicateurs clés (st.metric dans st.columns)
# ---------------------------------------------------------
st.markdown("---")
st.subheader("📊 Indicateurs clés (sélection active)")

col1, col2, col3, col4 = st.columns(4)

prod_totale = df_filtre["production_t"].sum()
valeur_totale_mrd = df_filtre["valeur_htg"].sum() / 1e9
surface_totale = df_filtre["surface_ha"].sum()
rendement_moyen = prod_totale / surface_totale if surface_totale > 0 else 0

with col1:
    st.metric(
        label="Production totale",
        value=f"{prod_totale:,.0f} t".replace(",", " "),
        help="Volume total récolté en tonnes",
    )

with col2:
    st.metric(
        label="Valeur économique",
        value=f"{valeur_totale_mrd:.2f} Mrd HTG",
        help="Valeur marchande totale estimée en milliards de gourdes",
    )

with col3:
    st.metric(
        label="Surface cultivée",
        value=f"{surface_totale:,.0f} ha".replace(",", " "),
        help="Superficie totale emblavée en hectares",
    )

with col4:
    st.metric(
        label="Rendement global moyen",
        value=f"{rendement_moyen:.2f} t/ha",
        help="Rendement moyen pondéré (production totale / surface totale)",
    )

st.markdown("---")

# ---------------------------------------------------------
# Étape 5 : Onglets par question (st.tabs)
# ---------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "1. Poids & Valeur",
    "2. Rendements par département",
    "3. Pluie & Rendements",
    "4. Dynamique 2023–2025",
    "5. Production par habitant",
])

# Style graphique uniforme
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

# --- ONGLET 1 : Poids en tonnes vs Valeur ---
with tab1:
    st.subheader("1. Poids physique en tonnes vs Valeur économique en gourdes")
    
    q1 = df_filtre.groupby("culture")[["production_t", "valeur_htg"]].sum().reset_index()
    q1["valeur_mrd"] = q1["valeur_htg"] / 1e9
    q1["part_prod_%"] = (q1["production_t"] / q1["production_t"].sum()) * 100
    q1["part_val_%"] = (q1["valeur_mrd"] / q1["valeur_mrd"].sum()) * 100
    
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        q1_t = q1.sort_values(by="production_t", ascending=True)
        fig1, ax1 = plt.subplots(figsize=(6, 4))
        bars1 = ax1.barh(q1_t["culture"], q1_t["production_t"] / 1e3, color="#2b5c8f")
        ax1.set_xlabel("Production (milliers de tonnes)")
        ax1.set_title("Production totale par culture (k tonnes)", fontweight="bold")
        for bar in bars1:
            w = bar.get_width()
            ax1.text(w + 2, bar.get_y() + bar.get_height() / 2, f"{w:.1f}k", va="center", fontsize=9)
        ax1.set_xlim(0, (q1_t["production_t"].max() / 1e3) * 1.18)
        fig1.tight_layout()
        st.pyplot(fig1)
        plt.close(fig1)

    with col_g2:
        q1_v = q1.sort_values(by="valeur_mrd", ascending=True)
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        bars2 = ax2.barh(q1_v["culture"], q1_v["valeur_mrd"], color="#2e7d32")
        ax2.set_xlabel("Valeur (Milliards HTG)")
        ax2.set_title("Valeur économique par culture (Mrd HTG)", fontweight="bold")
        for bar in bars2:
            w = bar.get_width()
            ax2.text(w + 0.2, bar.get_y() + bar.get_height() / 2, f"{w:.2f}", va="center", fontsize=9)
        ax2.set_xlim(0, q1_v["valeur_mrd"].max() * 1.18)
        fig2.tight_layout()
        st.pyplot(fig2)
        plt.close(fig2)

    # Tableau comparatif des rangs
    q1_table = q1.copy()
    q1_table["Rang Volume"] = q1_table["production_t"].rank(ascending=False).astype(int)
    q1_table["Rang Valeur"] = q1_table["valeur_htg"].rank(ascending=False).astype(int)
    q1_table = q1_table.sort_values("Rang Volume").rename(columns={
        "culture": "Culture",
        "production_t": "Production (t)",
        "part_prod_%": "Part Volume (%)",
        "valeur_mrd": "Valeur (Mrd HTG)",
        "part_val_%": "Part Valeur (%)",
    })
    st.dataframe(
        q1_table[["Culture", "Production (t)", "Part Volume (%)", "Valeur (Mrd HTG)", "Part Valeur (%)", "Rang Volume", "Rang Valeur"]].style.format({
            "Production (t)": "{:,.0f}",
            "Part Volume (%)": "{:.1f}%",
            "Valeur (Mrd HTG)": "{:.2f}",
            "Part Valeur (%)": "{:.1f}%",
        }),
        hide_index=True,
        use_container_width=True,
    )

    st.info(
        "💡 **Ce qu'on en conclut :** Le classement change significativement entre volume et valeur marchande ! "
        "Si la banane domine le tonnage (41,4 % avec 547 615 t), l'igname s'impose au 1er rang économique avec "
        "12,07 milliards HTG (37,1 % de la valeur marchande totale) grâce à un prix de 30 HTG/kg. "
        "Les légumineuses (haricot, pois congo) tirent leur épingle du jeu : le haricot, bien que 7e en tonnage (3,2 %), "
        "remonte au 5e rang en valeur avec un prix record de 65 HTG/kg."
    )

# --- ONGLET 2 : Rendements par département ---
with tab2:
    st.subheader("2. Rendements moyens (t/ha) par département et culture")
    
    culture_choisie = st.selectbox(
        "Sélectionnez une culture à observer en détail :",
        options=toutes_cultures,
        index=0,
    )
    
    df_cult = df_filtre[df_filtre["culture"] == culture_choisie]
    
    if not df_cult.empty:
        rend_dep = df_cult.groupby("departement").apply(
            lambda g: g["production_t"].sum() / g["surface_ha"].sum(),
            include_groups=False,
        ).reset_index(name="rendement_t_ha").sort_values(by="rendement_t_ha", ascending=True)
        
        fig, ax = plt.subplots(figsize=(9, 4.5))
        bars = ax.barh(rend_dep["departement"], rend_dep["rendement_t_ha"], color="#d95f02")
        ax.set_xlabel("Rendement moyen pondéré (t/ha)")
        ax.set_title(f"Rendements moyens de la culture : {culture_choisie}", fontweight="bold")
        for bar in bars:
            w = bar.get_width()
            ax.text(w + 0.05, bar.get_y() + bar.get_height() / 2, f"{w:.2f}", va="center", fontsize=9)
        ax.set_xlim(0, rend_dep["rendement_t_ha"].max() * 1.15)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.write("Aucune donnée pour cette culture avec les filtres actuels.")

    # Synthèse générale globale
    st.markdown("#### Panorama global des meilleurs départements par culture (sur l'ensemble des données)")
    vue_globale = pd.DataFrame([
        {"Culture": "Maïs", "Meilleur département": "Centre", "Rendement max (t/ha)": 1.20, "Département le plus faible": "Nord-Est", "Rendement min (t/ha)": 0.91},
        {"Culture": "Sorgho", "Meilleur département": "Centre", "Rendement max (t/ha)": 1.08, "Département le plus faible": "Nord-Est", "Rendement min (t/ha)": 0.77},
        {"Culture": "Riz", "Meilleur département": "Artibonite", "Rendement max (t/ha)": 3.80, "Département le plus faible": "Nord-Est", "Rendement min (t/ha)": 2.12},
        {"Culture": "Haricot", "Meilleur département": "Sud", "Rendement max (t/ha)": 0.88, "Département le plus faible": "Nord-Ouest", "Rendement min (t/ha)": 0.60},
        {"Culture": "Pois congo", "Meilleur département": "Nord-Ouest", "Rendement max (t/ha)": 1.01, "Département le plus faible": "Nord-Est", "Rendement min (t/ha)": 0.63},
        {"Culture": "Banane", "Meilleur département": "Nord", "Rendement max (t/ha)": 9.05, "Département le plus faible": "Nord-Est", "Rendement min (t/ha)": 6.23},
        {"Culture": "Igname", "Meilleur département": "Grand'Anse", "Rendement max (t/ha)": 8.24, "Département le plus faible": "Nippes", "Rendement min (t/ha)": 5.30},
    ])
    st.dataframe(vue_globale, hide_index=True, use_container_width=True)

    st.info(
        "💡 **Ce qu'on en conclut :** La productivité est fortement territorialisée : "
        "l'Artibonite est le leader incontesté du riz avec 3,80 t/ha (système irrigué de la basse vallée), "
        "le Centre enregistre les meilleurs rendements en céréales sèches (maïs à 1,20 t/ha, sorgho à 1,08 t/ha), "
        "le Nord et la Grand'Anse mènent sur les cultures humides pérennes et tubercules (9,05 t/ha pour la banane, 8,24 t/ha pour l'igname). "
        "À l'inverse, le Nord-Est est en queue de peloton sur 5 des 7 cultures en raison de contraintes édaphiques et hydriques."
    )

# --- ONGLET 3 : Pluie et rendements ---
with tab3:
    st.subheader("3. Influence de la pluviométrie saisonnière sur les rendements")
    
    cult_scatter = st.selectbox(
        "Culture à observer en nuage de points :",
        options=toutes_cultures,
        index=0,
        key="scatter_cult",
    )
    
    df_scat = df_filtre[df_filtre["culture"] == cult_scatter]
    
    if len(df_scat) > 3:
        corr_val = df_scat["pluie_mm"].corr(df_scat["rendement_t_ha"])
        
        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.scatter(df_scat["pluie_mm"], df_scat["rendement_t_ha"], color="#1f77b4", alpha=0.7, edgecolors="k", s=50)
        
        # Ligne de tendance linéaire
        m, b = np.polyfit(df_scat["pluie_mm"], df_scat["rendement_t_ha"], 1)
        x_vals = np.linspace(df_scat["pluie_mm"].min(), df_scat["pluie_mm"].max(), 50)
        ax.plot(x_vals, m * x_vals + b, color="#d62728", linestyle="--", linewidth=2, label=f"Tendance linéaire (r = {corr_val:.2f})")
        
        ax.set_xlabel("Pluviométrie saisonnière (mm)")
        ax.set_ylabel("Rendement (t/ha)")
        ax.set_title(f"Pluie vs Rendement pour {cult_scatter} (r = {corr_val:.2f})", fontweight="bold")
        ax.legend()
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.write("Pas assez de points pour afficher le nuage et la droite de tendance.")

    # Tableau récapitulatif des corrélations sur le jeu complet
    corrs = []
    for c in toutes_cultures:
        sub_c = df[df["culture"] == c]
        r = sub_c["pluie_mm"].corr(sub_c["rendement_t_ha"])
        corrs.append({"Culture": c, "Corrélation de Pearson (r)": round(r, 3), "Sensibilité à la pluie": "Très forte" if r > 0.7 else "Modérée" if r > 0.5 else "Faible"})
    
    df_corrs = pd.DataFrame(corrs).sort_values("Corrélation de Pearson (r)", ascending=False)
    st.markdown("#### Coefficients de corrélation par culture :")
    st.dataframe(df_corrs, hide_index=True, use_container_width=True)

    st.info(
        "💡 **Ce qu'on en conclut :** La pluie explique une part prépondérante du rendement pour les cultures vivrières "
        "strictement pluviales : le haricot (r = 0,76) et le maïs (r = 0,76) affichent une dépendance très forte. "
        "En revanche, la pluie locale n'explique que faiblement le rendement du riz (r = 0,42) : la culture rizicole, "
        "concentrée dans l'Artibonite, est régulée par le système d'irrigation alimenté par le fleuve Artibonite et les barrages, "
        "décorrélant ainsi sa productivité des précipitations directes de la saison."
    )

# --- ONGLET 4 : Dynamique 2023-2025 ---
with tab4:
    st.subheader("4. Trajectoires et évolution des cultures entre 2023 et 2025")
    
    pivot_prod = df.pivot_table(index="culture", columns="annee", values="production_t", aggfunc="sum").reset_index()
    pivot_prod["Évolution (%)"] = ((pivot_prod[2025] - pivot_prod[2023]) / pivot_prod[2023]) * 100
    pivot_prod["Variation (tonnes)"] = pivot_prod[2025] - pivot_prod[2023]
    pivot_prod = pivot_prod.sort_values(by="Évolution (%)", ascending=False)
    
    fig, ax = plt.subplots(figsize=(9, 4.5))
    couleurs = ["#2ca02c" if x >= 0 else "#d62728" for x in pivot_prod["Évolution (%)"]]
    bars = ax.bar(pivot_prod["culture"], pivot_prod["Évolution (%)"], color=couleurs, edgecolor="black", alpha=0.85)
    ax.axhline(0, color="black", linewidth=1)
    ax.set_ylabel("Évolution de la production 2023 -> 2025 (%)")
    ax.set_title("Progression ou recul de la production entre 2023 et 2025 (%)", fontweight="bold")
    for bar in bars:
        h = bar.get_height()
        va = "bottom" if h >= 0 else "top"
        ax.text(bar.get_x() + bar.get_width() / 2, h + (1 if h >= 0 else -3), f"{h:+.1f}%", ha="center", va=va, fontweight="bold", fontsize=9)
    ax.set_ylim(min(pivot_prod["Évolution (%)"].min() - 8, -40), max(pivot_prod["Évolution (%)"].max() + 8, 25))
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    st.dataframe(
        pivot_prod.rename(columns={2023: "Production 2023 (t)", 2024: "Production 2024 (t)", 2025: "Production 2025 (t)"}).style.format({
            "Production 2023 (t)": "{:,.0f}",
            "Production 2024 (t)": "{:,.0f}",
            "Production 2025 (t)": "{:,.0f}",
            "Évolution (%)": "{:+.1f}%",
            "Variation (tonnes)": "{:+,.0f}",
        }),
        hide_index=True,
        use_container_width=True,
    )

    st.info(
        "💡 **Ce qu'on en conclut :** Deux dynamiques opposées se dessinent nettement : "
        "d'un côté, le riz (+19,1 %, +8 437 t), le sorgho (+17,6 %, +3 613 t) et la banane (+8,4 %, +15 430 t) progressent fermement. "
        "De l'autre côté, l'igname subit un recul spectaculaire de -32,2 % (-52 115 t), principalement causé par un délaissement des surfaces "
        "cultivées (-31,5 % d'hectares). Le maïs (-11,2 %) et le haricot (-12,4 %) reculent également, fragilisant la souveraineté alimentaire sur ces bases."
    )

# --- ONGLET 5 : Production par habitant ---
with tab5:
    st.subheader("5. Production vivrière rapportée à la population départementale")
    
    prod_hab = df.groupby(["departement", "population"])["production_t"].sum().reset_index()
    prod_hab["prod_kg"] = prod_hab["production_t"] * 1000
    prod_hab["kg_par_hab_3ans"] = prod_hab["prod_kg"] / prod_hab["population"]
    prod_hab["kg_par_hab_an"] = prod_hab["kg_par_hab_3ans"] / 3.0
    prod_hab = prod_hab.sort_values(by="kg_par_hab_an", ascending=True)
    
    fig, ax = plt.subplots(figsize=(9, 4.5))
    bars = ax.barh(prod_hab["departement"], prod_hab["kg_par_hab_an"], color="#8c564b")
    ax.set_xlabel("Production annuelle moyenne par habitant (kg / hab / an)")
    ax.set_title("Production vivrière par habitant et par an selon le département", fontweight="bold")
    for bar in bars:
        w = bar.get_width()
        ax.text(w + 1, bar.get_y() + bar.get_height() / 2, f"{w:.1f} kg/an", va="center", fontsize=9)
    ax.set_xlim(0, prod_hab["kg_par_hab_an"].max() * 1.18)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    st.dataframe(
        prod_hab.sort_values(by="kg_par_hab_an", ascending=False).rename(columns={
            "departement": "Département",
            "population": "Population",
            "production_t": "Production totale 3 ans (t)",
            "kg_par_hab_3ans": "Total 3 ans (kg/hab)",
            "kg_par_hab_an": "Moyenne annuelle (kg/hab/an)",
        }).style.format({
            "Population": "{:,.0f}",
            "Production totale 3 ans (t)": "{:,.0f}",
            "Total 3 ans (kg/hab)": "{:.1f}",
            "Moyenne annuelle (kg/hab/an)": "{:.1f}",
        }),
        hide_index=True,
        use_container_width=True,
    )

    st.info(
        "💡 **Ce qu'on en conclut :** La Grand'Anse arrive en tête avec 81,4 kg/hab/an (244,3 kg sur 3 ans), "
        "suivie du Centre (74,6 kg/hab/an) et du Sud (66,7 kg/hab/an). Ces trois départements jouent un rôle vital de greniers vivriers. "
        "En revanche, l'Ouest ferme la marche avec seulement 16,9 kg/hab/an (50,8 kg sur 3 ans) en raison de sa forte concentration urbaine "
        "(plus de 4 millions d'habitants à Port-au-Prince), créant une dépendance quasi-totale envers les corridors d'approvisionnement interdépartementaux."
    )

# ---------------------------------------------------------
# Étape 6 : Conclusion, limites et expander des données
# ---------------------------------------------------------
st.markdown("---")
st.subheader("📌 Conclusion stratégique et limites des données")

col_c1, col_c2 = st.columns(2)

with col_c1:
    st.markdown("### Ce qu'il faut retenir")
    st.markdown(
        """
        1. **Poids et valeur :** La banane domine en tonnage (41,4 %), mais l'igname est le premier moteur économique (37,1 % de la valeur, 12 Mrd HTG). Le haricot offre la plus haute valeur unitaire (65 HTG/kg).
        2. **Spécialisation géographique :** L'Artibonite concentre les rendements en riz (3,80 t/ha), le Centre en céréales sèches, la Grand'Anse et le Nord en cultures arborées et tubercules. Le Nord-Est accuse un retard structurel.
        3. **Sensibilité climatique :** Les cultures pluviales (haricot, maïs) sont tributaires de la pluie (r > 0,75), rendant les récoltes vulnérables aux aléas météo, contrairement au riz irrigué.
        4. **Alerte sur les tubercules :** L'igname a perdu 32 % de sa production en deux ans par abandon des surfaces, signalant un risque d'érosion des revenus paysans.
        5. **Déséquilibre démographique :** L'Ouest ne produit que 17 kg/hab/an, ce qui impose de sécuriser les voies logistiques depuis les départements excédentaires (Grand'Anse, Centre, Sud).
        """
    )

with col_c2:
    st.markdown("### Limites des données et perspectives")
    st.markdown(
        """
        - **Prix supposés constants :** Les prix sont fixés au niveau national et n'intègrent ni l'inflation (forte en Haïti) ni les variations locales et saisonnières de marché.
        - **Échelle départementale agrégée :** L'agrégation par département masque les poches de sécheresse microclimatiques et les disparités entre communes.
        - **Absence des coûts d'exploitation :** Nous disposons du chiffre d'affaires brut mais pas des marges nettes paysannes (coût des semences, engrais, main-d'œuvre, transport).
        - **À mesurer ensuite :** Enquêtes sur le coût des intrants, suivi de l'humidité des sols par satellite, et suivi des pertes post-récolte pour orienter les investissements publics.
        """
    )

with st.expander("🔎 Consulter et télécharger les données filtrées"):
    st.write(f"Nombre d'enregistrements correspondant aux filtres : **{len(df_filtre)}** sur {len(df)}")
    st.dataframe(df_filtre, hide_index=True, use_container_width=True)
    
    csv_data = df_filtre.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Télécharger la sélection en CSV",
        data=csv_data,
        file_name="recoltes_selectionnees.csv",
        mime="text/csv",
    )
