from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Télécom Maroc - Analyse de Sentiments",
    page_icon="📶",
    layout="wide",
    initial_sidebar_state="expanded"
)

COLOR_MAP = {
    "IAM": "#005C9E",
    "Orange": "#FF7900",
    "INWI": "#8A157C",
    "Global": "#2C3E50"
}

st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #FFFFFF;
        padding: 1.2rem;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        border: 1px solid #E2E8F0;
        text-align: center;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px;
        border-radius: 6px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    base_dir = Path(__file__).resolve().parent
    dw_dir = base_dir / "data" / "dw_output"

    required_files = [
        "fact_reviews.csv",
        "dim_operateur.csv",
        "dim_ville.csv",
        "dim_temps.csv",
        "dim_topic.csv",
        "dim_agence.csv",
        "dim_reviews.csv"
    ]
    for f in required_files:
        if not (dw_dir / f).exists():
            st.error(f"Fichier manquant : {dw_dir / f}.")
            st.stop()

    fact = pd.read_csv(dw_dir / "fact_reviews.csv")
    dim_op = pd.read_csv(dw_dir / "dim_operateur.csv")
    dim_ville = pd.read_csv(dw_dir / "dim_ville.csv")
    dim_temps = pd.read_csv(dw_dir / "dim_temps.csv")
    dim_topic = pd.read_csv(dw_dir / "dim_topic.csv")
    dim_agence = pd.read_csv(dw_dir / "dim_agence.csv")
    dim_reviews = pd.read_csv(dw_dir / "dim_reviews.csv")

    df = fact.merge(dim_op, on="operateur_id", how="left")
    df = df.merge(dim_ville, on="ville_id", how="left")
    df = df.merge(dim_temps, on="temps_id", how="left")
    df = df.merge(dim_topic, on="topic_id", how="left")
    df = df.merge(dim_agence[["agence_id", "nom_agence", "adresse"]], on="agence_id", how="left")
    df = df.merge(dim_reviews[["review_id", "Comment"]], on="review_id", how="left")

    df["review_year"] = pd.to_numeric(df["review_year"], errors="coerce")
    df["review_month"] = pd.to_numeric(df["review_month"], errors="coerce")
    df["review_day"] = pd.to_numeric(df["review_day"], errors="coerce")

    df["date"] = pd.to_datetime(
        df["review_year"].astype("Int64").astype(str) + "-" +
        df["review_month"].astype("Int64").astype(str).str.zfill(2) + "-" +
        df["review_day"].astype("Int64").astype(str).str.zfill(2),
        errors="coerce"
    )
    df["periode"] = (
        df["review_year"].astype("Int64").astype(str) + "-" +
        df["review_month"].astype("Int64").astype(str).str.zfill(2)
    )

    df["operateur_name"] = df["operateur_name"].fillna("Inconnu").str.strip()
    df["ville"] = df["ville"].fillna("Non précisée").str.strip()
    df["topic"] = df["topic"].fillna("autre").str.strip()

    return df

df_all = load_data()

with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/signal-coverage.png", width=64)
    st.title("Télécom Maroc")
    st.markdown("**Observatoire des Sentiments Clients**")
    st.markdown("---")

    st.subheader("⚙️ Filtres Globaux")

    years_available = sorted([int(y) for y in df_all["review_year"].dropna().unique()])
    selected_years = st.multiselect(
        "Année(s) :",
        options=years_available,
        default=years_available
    )

    sentiment_range = st.slider(
        "Plage de sentiment :",
        min_value=-1.0,
        max_value=1.0,
        value=(-1.0, 1.0),
        step=0.05
    )

    st.markdown("---")
    st.markdown("""
    **Modèle de Données :**
    - Star Schema (PostgreSQL)
    - IA : NLP Hugging Face Transformers
    - Opérateurs : IAM, Orange, inwi
    """)

df_filtered = df_all[
    (df_all["review_year"].isin(selected_years)) &
    (df_all["sentiment_score"] >= sentiment_range[0]) &
    (df_all["sentiment_score"] <= sentiment_range[1])
].copy()

df_distinct_reviews = df_filtered.drop_duplicates(subset=["review_id"]).copy()

st.markdown('<div class="main-title">📊 Analyse de Sentiment des Avis Clients - Télécom Maroc</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Visualisation interactive des scores de sentiment Google Maps pour Maroc Telecom (IAM), Orange Maroc et inwi.</div>', unsafe_allow_html=True)

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

total_reviews = len(df_distinct_reviews)
avg_score_global = df_distinct_reviews["sentiment_score"].mean()

op_scores = df_distinct_reviews.groupby("operateur_name")["sentiment_score"].mean()
best_op = op_scores.idxmax() if not op_scores.empty else "N/A"
best_score = op_scores.max() if not op_scores.empty else 0.0

top_topic = df_distinct_reviews["topic"].value_counts().idxmax() if not df_distinct_reviews.empty else "N/A"

with kpi1:
    st.metric(label="Total Avis Clients", value=f"{total_reviews:,}".replace(",", " "))
with kpi2:
    st.metric(label="Score Moyen Global", value=f"{avg_score_global:.2f}", delta=f"{'Positif' if avg_score_global > 0 else 'Négatif'}")
with kpi3:
    st.metric(label="Meilleur Opérateur", value=best_op, delta=f"{best_score:.2f}")
with kpi4:
    st.metric(label="Sujet le Plus Évoqué", value=top_topic.split()[0].capitalize())

st.markdown("---")

st.subheader("1. ⚖️ Comparaison Globale des Sentiments entre les Opérateurs")
st.markdown("Score de sentiment moyen calculé sur l'ensemble des avis pour chaque opérateur (échelle de -1.0 à +1.0).")

op_agg = df_distinct_reviews.groupby("operateur_name").agg(
    score_moyen=("sentiment_score", "mean"),
    total_avis=("review_id", "count"),
    avis_positifs=("sentiment_score", lambda x: (x > 0.1).sum()),
    avis_negatifs=("sentiment_score", lambda x: (x < -0.1).sum()),
    avis_neutres=("sentiment_score", lambda x: ((x >= -0.1) & (x <= 0.1)).sum())
).reset_index()

op_agg["taux_positif"] = (op_agg["avis_positifs"] / op_agg["total_avis"] * 100).round(1)

fig_op = go.Figure()
for _, row in op_agg.iterrows():
    op_name = row["operateur_name"]
    score = row["score_moyen"]
    fig_op.add_trace(go.Bar(
        x=[op_name],
        y=[score],
        name=op_name,
        marker=dict(
            color=COLOR_MAP.get(op_name, "#2C3E50"),
            line=dict(color="#1E293B", width=1.5)
        ),
        text=[f"{score:+.2f} ({row['total_avis']} avis)"],
        textposition="outside",
        hovertemplate=(
            f"<b>{op_name}</b><br>" +
            f"Score Moyen : {score:.2f}<br>" +
            f"Nombre d'avis : {row['total_avis']}<br>" +
            f"Taux d'avis positifs : {row['taux_positif']}%<extra></extra>"
        )
    ))

fig_op.update_layout(
    height=420,
    yaxis=dict(title="Score de Sentiment Moyen", range=[-1.0, 1.0], zeroline=True, zerolinewidth=2, zerolinecolor="black"),
    xaxis=dict(title="Opérateur Télécom"),
    showlegend=False,
    template="plotly_white",
    margin=dict(l=40, r=40, t=20, b=40)
)
st.plotly_chart(fig_op, use_container_width=True)

st.dataframe(
    op_agg.rename(columns={
        "operateur_name": "Opérateur",
        "score_moyen": "Score Moyen",
        "total_avis": "Nombre d'Avis",
        "avis_positifs": "Avis Positifs",
        "avis_negatifs": "Avis Négatifs",
        "avis_neutres": "Avis Neutres",
        "taux_positif": "Taux Satisfaction (%)"
    }).style.format({
        "Score Moyen": "{:+.2f}",
        "Taux Satisfaction (%)": "{:.1f}%"
    }),
    use_container_width=True
)

st.markdown("---")

st.subheader("2. 🏙️ Analyse du Sentiment par Ville")
st.markdown("Comparaison des scores de perception client selon les agences réparties dans les différentes villes marocaines.")

col_sel_ville, _ = st.columns([1, 2])
with col_sel_ville:
    op_list_ville = ["Tous les opérateurs"] + sorted(df_filtered["operateur_name"].unique().tolist())
    selected_op_ville = st.selectbox(
        "Choisir l'opérateur à analyser :",
        options=op_list_ville,
        key="sel_ville"
    )

if selected_op_ville == "Tous les opérateurs":
    df_city_src = df_filtered.copy()
    bar_color = "#34495E"
else:
    df_city_src = df_filtered[df_filtered["operateur_name"] == selected_op_ville].copy()
    bar_color = COLOR_MAP.get(selected_op_ville, "#34495E")

df_city_clean = df_city_src.drop_duplicates(subset=["review_id", "ville"])

city_agg = df_city_clean.groupby("ville").agg(
    score_moyen=("sentiment_score", "mean"),
    total_avis=("review_id", "count")
).reset_index()

city_agg = city_agg[city_agg["total_avis"] > 0].sort_values("score_moyen", ascending=True)

if not city_agg.empty:
    fig_city = px.bar(
        city_agg,
        x="score_moyen",
        y="ville",
        orientation="h",
        text=city_agg["score_moyen"].apply(lambda x: f"{x:+.2f}"),
        color="score_moyen",
        color_continuous_scale="RdYlGn",
        range_color=[-0.8, 0.8],
        title=f"Score de Sentiment par Ville - {selected_op_ville}",
        labels={"score_moyen": "Score Moyen", "ville": "Ville", "total_avis": "Avis"},
        hover_data={"total_avis": True, "score_moyen": ":.2f"}
    )
    fig_city.update_layout(
        height=max(400, len(city_agg) * 28),
        xaxis=dict(range=[-1.0, 1.0], zeroline=True, zerolinewidth=1.5, zerolinecolor="black"),
        template="plotly_white",
        margin=dict(l=40, r=40, t=40, b=40)
    )
    st.plotly_chart(fig_city, use_container_width=True)
else:
    st.warning("Aucune donnée disponible pour cette sélection.")

st.markdown("---")

st.subheader("3. 🎯 Répartition Globale des Sujets Abordés (Topics)")
st.markdown("Part relative de chaque catégorie thématique identifiée par le modèle NLP Zero-Shot dans l'ensemble des avis clients.")

df_topic_global = df_distinct_reviews.copy()
topic_counts = df_topic_global["topic"].value_counts().reset_index()
topic_counts.columns = ["topic", "count"]

fig_pie_global = px.pie(
    topic_counts,
    names="topic",
    values="count",
    hole=0.4,
    title="Répartition Globale des Topics (Tous Opérateurs Confondus)",
    color_discrete_sequence=px.colors.qualitative.Prism
)
fig_pie_global.update_traces(
    textposition="inside",
    textinfo="percent+label",
    hovertemplate="<b>%{label}</b><br>Nombre d'avis : %{value}<br>Pourcentage : %{percent}<extra></extra>"
)
fig_pie_global.update_layout(
    height=480,
    showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
    margin=dict(l=40, r=40, t=50, b=80)
)
st.plotly_chart(fig_pie_global, use_container_width=True)

st.markdown("---")

st.subheader("4. 🔍 Répartition des Topics par Opérateur")
st.markdown("Analyse spécifique des sujets de réclamation et d'appréciation pour chaque opérateur pris individuellement.")

col_sel_topic, _ = st.columns([1, 2])
with col_sel_topic:
    selected_op_topic = st.selectbox(
        "Choisir l'opérateur pour l'analyse des sujets :",
        options=["IAM", "Orange", "INWI"],
        key="sel_op_topic"
    )

df_op_topic = df_distinct_reviews[df_distinct_reviews["operateur_name"] == selected_op_topic].copy()
topic_op_counts = df_op_topic["topic"].value_counts().reset_index()
topic_op_counts.columns = ["topic", "count"]

if not topic_op_counts.empty:
    fig_pie_op = px.pie(
        topic_op_counts,
        names="topic",
        values="count",
        hole=0.4,
        title=f"Répartition des Sujets pour {selected_op_topic} ({len(df_op_topic)} avis)",
        color_discrete_sequence=px.colors.qualitative.Safe
    )
    fig_pie_op.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>Avis : %{value}<br>Part : %{percent}<extra></extra>"
    )
    fig_pie_op.update_layout(
        height=480,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
        margin=dict(l=40, r=40, t=50, b=80)
    )
    st.plotly_chart(fig_pie_op, use_container_width=True)
else:
    st.warning("Aucun avis disponible pour cet opérateur.")

st.markdown("---")

st.subheader("5. 📈 Évolution Temporelle du Sentiment")
st.markdown("Suivi des tendances et des variations du sentiment client au cours du temps (agrégation par mois).")

col_sel_time, col_granularity = st.columns([1, 1])
with col_sel_time:
    op_list_time = ["Tous les opérateurs (Comparaison)", "IAM", "Orange", "INWI"]
    selected_op_time = st.selectbox(
        "Opérateur(s) à afficher dans la tendance :",
        options=op_list_time,
        key="sel_op_time"
    )

with col_granularity:
    granularity = st.radio(
        "Période d'agrégation :",
        options=["Mois (YYYY-MM)", "Année (YYYY)"],
        horizontal=True
    )

time_col = "periode" if "Mois" in granularity else "review_year"

fig_trend = go.Figure()

if selected_op_time == "Tous les opérateurs (Comparaison)":
    for op in ["IAM", "Orange", "INWI"]:
        df_sub = df_distinct_reviews[df_distinct_reviews["operateur_name"] == op]
        trend = df_sub.groupby(time_col).agg(
            score_moyen=("sentiment_score", "mean"),
            total=("review_id", "count")
        ).reset_index().dropna().sort_values(time_col)

        fig_trend.add_trace(go.Scatter(
            x=trend[time_col].astype(str),
            y=trend["score_moyen"],
            mode="lines+markers",
            name=op,
            line=dict(color=COLOR_MAP.get(op, "#2C3E50"), width=2.5),
            marker=dict(size=6),
            hovertemplate=(
                f"<b>{op}</b> (%{{x}})<br>" +
                "Score : %{y:.2f}<br>" +
                "Avis : %{customdata}<extra></extra>"
            ),
            customdata=trend["total"]
        ))
else:
    df_sub = df_distinct_reviews[df_distinct_reviews["operateur_name"] == selected_op_time]
    trend = df_sub.groupby(time_col).agg(
        score_moyen=("sentiment_score", "mean"),
        total=("review_id", "count")
    ).reset_index().dropna().sort_values(time_col)

    op_color = COLOR_MAP.get(selected_op_time, "#2C3E50")
    fig_trend.add_trace(go.Scatter(
        x=trend[time_col].astype(str),
        y=trend["score_moyen"],
        mode="lines+markers",
        name=selected_op_time,
        line=dict(color=op_color, width=3),
        marker=dict(size=7, color=op_color),
        fill="tozeroy",
        fillcolor="rgba(0,0,0,0.04)",
        hovertemplate=(
            f"<b>{selected_op_time}</b> (%{{x}})<br>" +
            "Score : %{y:.2f}<br>" +
            "Avis : %{customdata}<extra></extra>"
        ),
        customdata=trend["total"]
    ))

fig_trend.update_layout(
    title=f"Tendance du Sentiment - {selected_op_time}",
    xaxis=dict(title="Période", tickangle=-45),
    yaxis=dict(title="Score Moyen de Sentiment", range=[-1.0, 1.0], zeroline=True, zerolinewidth=1.5, zerolinecolor="black"),
    template="plotly_white",
    height=450,
    hovermode="x unified",
    margin=dict(l=40, r=40, t=40, b=60)
)
st.plotly_chart(fig_trend, use_container_width=True)

st.markdown("---")

with st.expander("🔎 Explorateur d'Avis Clients Réels (Table de Dimensions dim_reviews)"):
    st.markdown("Consultez et filtrez les avis Google Maps réels enregistrés dans la dimension `dim_reviews`.")

    exp_col1, exp_col2, exp_col3 = st.columns(3)
    with exp_col1:
        filter_op = st.selectbox("Filtrer par opérateur :", ["Tous"] + ["IAM", "Orange", "INWI"])
    with exp_col2:
        filter_topic = st.selectbox("Filtrer par sujet :", ["Tous"] + sorted(df_distinct_reviews["topic"].unique().tolist()))
    with exp_col3:
        search_kw = st.text_input("Recherche par mot-clé :", placeholder="ex: fibre, guichet, facture...")

    df_sample = df_distinct_reviews.copy()
    if filter_op != "Tous":
        df_sample = df_sample[df_sample["operateur_name"] == filter_op]
    if filter_topic != "Tous":
        df_sample = df_sample[df_sample["topic"] == filter_topic]
    if search_kw:
        df_sample = df_sample[df_sample["Comment"].astype(str).str.contains(search_kw, case=False, na=False)]

    cols_to_show = ["operateur_name", "ville", "topic", "sentiment_score", "Comment"]
    st.dataframe(
        df_sample[cols_to_show].head(100).rename(columns={
            "operateur_name": "Opérateur",
            "ville": "Ville",
            "topic": "Sujet",
            "sentiment_score": "Score",
            "Comment": "Avis Client"
        }),
        use_container_width=True,
        height=320
    )

st.caption("Projet Data Engineering & Sentiment Analysis - Schéma en Étoile (Star Schema) - Télécom Maroc")
