"""
Dashboard d'analyse des sentiments - Télécom Maroc
Opérateurs : IAM (Maroc Telecom), Orange Maroc, inwi
Source : schéma en étoile (data/dw_output)
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ==============================================================================
# 1. CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="Sentiments clients - Télécom Maroc",
    page_icon="📶",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Couleurs de marque (clés en minuscules pour tolérer IAM / Iam / iam)
BRAND_COLORS = {"iam": "#005C9E", "orange": "#FF7900", "inwi": "#8A157C"}
FALLBACK_COLOR = "#64748B"

# Couleurs sémantiques du sentiment
SENTIMENT_COLORS = {"Positif": "#2E9E6B", "Neutre": "#CBD5E1", "Négatif": "#D6483E"}
SENTIMENT_ORDER = ["Positif", "Neutre", "Négatif"]
NEUTRAL_THRESHOLD = 0.1  # |score| <= 0.1 => neutre

INK = "#0F172A"
MUTED = "#64748B"
GRID = "#E2E8F0"


def brand(op: str) -> str:
    return BRAND_COLORS.get(str(op).strip().lower(), FALLBACK_COLOR)


def sentiment_label(score: float) -> str:
    if score > NEUTRAL_THRESHOLD:
        return "Positif"
    if score < -NEUTRAL_THRESHOLD:
        return "Négatif"
    return "Neutre"


st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"], .stApp { font-family: 'Inter', sans-serif; }

    /* Espacement général */
    .block-container { padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1280px; }
    #MainMenu, footer { visibility: hidden; }

    /* Titres */
    .page-title { font-size: 1.9rem; font-weight: 800; color: #0F172A; letter-spacing: -0.02em; margin: 0; }
    .page-sub   { font-size: 0.98rem; color: #64748B; margin: 0.25rem 0 1.4rem 0; }
    .section-note { color: #64748B; font-size: 0.92rem; margin: -0.2rem 0 0.8rem 0; }

    /* KPIs */
    [data-testid="stMetric"] {
        background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 10px;
        padding: 0.9rem 1.1rem;
    }
    [data-testid="stMetricLabel"] p { font-size: 0.82rem; color: #64748B; font-weight: 500; }
    [data-testid="stMetricValue"]   { font-size: 1.65rem; font-weight: 700; color: #0F172A; }

    /* Onglets */
    .stTabs [data-baseweb="tab-list"] { gap: 4px; border-bottom: 1px solid #E2E8F0; }
    .stTabs [data-baseweb="tab"] { padding: 0.55rem 1rem; font-weight: 500; }
    .stTabs [aria-selected="true"] { font-weight: 700; }

    /* Sidebar */
    [data-testid="stSidebar"] { border-right: 1px solid #E2E8F0; }
</style>
""",
    unsafe_allow_html=True,
)


# ==============================================================================
# 2. CHARGEMENT DES DONNÉES
# ==============================================================================
@st.cache_data(show_spinner="Chargement des données…")
def load_data() -> pd.DataFrame:
    """Charge les tables du schéma en étoile et reconstitue une vue à plat."""
    dw_dir = Path(__file__).resolve().parent / "data" / "dw_output"

    tables = {
        "fact": "fact_reviews.csv",
        "op": "dim_operateur.csv",
        "ville": "dim_ville.csv",
        "temps": "dim_temps.csv",
        "topic": "dim_topic.csv",
        "agence": "dim_agence.csv",
        "reviews": "dim_reviews.csv",
    }
    missing = [f for f in tables.values() if not (dw_dir / f).exists()]
    if missing:
        st.error(
            f"Fichiers manquants dans {dw_dir} : {', '.join(missing)}. "
            "Lancez d'abord `src/etl/build_data_warehouse.py`."
        )
        st.stop()

    t = {k: pd.read_csv(dw_dir / f) for k, f in tables.items()}

    df = (
        t["fact"]
        .merge(t["op"], on="operateur_id", how="left")
        .merge(t["ville"], on="ville_id", how="left")
        .merge(t["temps"], on="temps_id", how="left")
        .merge(t["topic"], on="topic_id", how="left")
        .merge(t["agence"][["agence_id", "nom_agence", "adresse"]], on="agence_id", how="left")
        .merge(t["reviews"][["review_id", "Comment"]], on="review_id", how="left")
    )

    # Dates
    for c in ("review_year", "review_month", "review_day"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["date"] = pd.to_datetime(
        {
            "year": df["review_year"],
            "month": df["review_month"].fillna(1),
            "day": df["review_day"].fillna(1),
        },
        errors="coerce",
    )
    df["mois"] = df["date"].dt.to_period("M").dt.to_timestamp()
    df["annee"] = df["date"].dt.to_period("Y").dt.to_timestamp()

    # Nettoyage
    df["operateur_name"] = df["operateur_name"].fillna("Inconnu").astype(str).str.strip()
    df["ville"] = df["ville"].fillna("Non précisée").astype(str).str.strip()
    df["topic"] = df["topic"].fillna("autre").astype(str).str.strip()
    df["sentiment_score"] = pd.to_numeric(df["sentiment_score"], errors="coerce")
    df = df.dropna(subset=["sentiment_score"])
    df["sentiment"] = df["sentiment_score"].apply(sentiment_label)

    return df


df_all = load_data()


# ==============================================================================
# 3. OUTILS GRAPHIQUES
# ==============================================================================
def style(fig: go.Figure, height: int = 380, legend: bool = False) -> go.Figure:
    """Habillage commun : fond transparent, grille discrète, police unique."""
    fig.update_layout(
        height=height,
        template="plotly_white",
        font=dict(family="Inter, sans-serif", size=13, color=INK),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=legend,
        hoverlabel=dict(bgcolor="white", font_size=13, bordercolor=GRID),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, title_text=""),
    )
    fig.update_xaxes(showline=False, gridcolor=GRID, zeroline=False, title_font=dict(color=MUTED))
    fig.update_yaxes(showline=False, gridcolor=GRID, zeroline=False, title_font=dict(color=MUTED))
    return fig


def show(fig: go.Figure) -> None:
    st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False, "displayModeBar": False})


def zero_line(fig: go.Figure, axis: str = "y") -> None:
    if axis == "y":
        fig.add_hline(y=0, line_width=1.2, line_color=INK, opacity=0.5)
    else:
        fig.add_vline(x=0, line_width=1.2, line_color=INK, opacity=0.5)


def empty_state(msg: str = "Aucune donnée pour cette sélection. Élargissez les filtres.") -> None:
    st.info(msg)


def section(title: str, note: str = "") -> None:
    st.markdown(f"### {title}")
    if note:
        st.markdown(f'<div class="section-note">{note}</div>', unsafe_allow_html=True)


# ==============================================================================
# 4. FILTRES (SIDEBAR)
# ==============================================================================
with st.sidebar:
    st.markdown("## Télécom Maroc")
    st.caption("Observatoire des sentiments clients")
    st.divider()

    years = sorted(int(y) for y in df_all["review_year"].dropna().unique())
    selected_years = st.multiselect("Années", years, default=years)

    all_ops = sorted(df_all["operateur_name"].unique())
    selected_ops = st.multiselect("Opérateurs", all_ops, default=all_ops)

    sentiment_range = st.slider("Plage de score de sentiment", -1.0, 1.0, (-1.0, 1.0), 0.05)

    st.divider()
    st.caption(
        "Score de -1 (très négatif) à +1 (très positif). "
        f"Neutre : entre -{NEUTRAL_THRESHOLD} et +{NEUTRAL_THRESHOLD}."
    )
    st.caption("Données : entrepôt en étoile · Analyse : modèles NLP Hugging Face.")

mask = (
    df_all["review_year"].isin(selected_years)
    & df_all["operateur_name"].isin(selected_ops)
    & df_all["sentiment_score"].between(*sentiment_range)
)
df_f = df_all[mask].copy()

# Un avis = une ligne (évite les doubles comptages liés aux jointures)
df_r = df_f.drop_duplicates(subset=["review_id"]).copy()

if df_r.empty:
    st.markdown('<div class="page-title">Sentiments clients · Télécom Maroc</div>', unsafe_allow_html=True)
    empty_state("Aucun avis ne correspond aux filtres actuels. Modifiez la sélection dans le panneau de gauche.")
    st.stop()


# ==============================================================================
# 5. EN-TÊTE + KPIs
# ==============================================================================
st.markdown('<div class="page-title">Sentiments clients · Télécom Maroc</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="page-sub">Avis Google Maps de Maroc Telecom (IAM), Orange Maroc et inwi, '
    "analysés par sentiment et par sujet.</div>",
    unsafe_allow_html=True,
)

op_means = df_r.groupby("operateur_name")["sentiment_score"].mean()
best_op, best_score = op_means.idxmax(), op_means.max()
top_topic = df_r["topic"].value_counts()
pct_pos = (df_r["sentiment"] == "Positif").mean() * 100
pct_neg = (df_r["sentiment"] == "Négatif").mean() * 100

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Avis analysés", f"{len(df_r):,}".replace(",", " "))
k2.metric("Score moyen", f"{df_r['sentiment_score'].mean():+.2f}")
k3.metric("Avis positifs", f"{pct_pos:.0f} %")
k4.metric("Avis négatifs", f"{pct_neg:.0f} %")
k5.metric("Opérateur le mieux noté", best_op, f"{best_score:+.2f}")

st.write("")

tab_ops, tab_villes, tab_sujets, tab_temps, tab_avis = st.tabs(
    ["Opérateurs", "Villes", "Sujets", "Évolution", "Avis"]
)


# ==============================================================================
# 6. ONGLET OPÉRATEURS
# ==============================================================================
with tab_ops:
    section("Comparaison des opérateurs", "Score moyen et répartition des avis par opérateur.")

    op_agg = (
        df_r.groupby("operateur_name")
        .agg(score_moyen=("sentiment_score", "mean"), total_avis=("review_id", "count"))
        .reset_index()
        .sort_values("score_moyen", ascending=False)
    )
    shares = (
        pd.crosstab(df_r["operateur_name"], df_r["sentiment"], normalize="index")
        .reindex(columns=SENTIMENT_ORDER, fill_value=0)
        * 100
    )
    op_agg = op_agg.merge(shares.reset_index(), on="operateur_name")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("**Score moyen**")
        fig = go.Figure(
            go.Bar(
                x=op_agg["operateur_name"],
                y=op_agg["score_moyen"],
                marker_color=[brand(o) for o in op_agg["operateur_name"]],
                text=op_agg["score_moyen"].map("{:+.2f}".format),
                textposition="outside",
                cliponaxis=False,
                customdata=op_agg["total_avis"],
                hovertemplate="<b>%{x}</b><br>Score moyen : %{y:+.2f}<br>Avis : %{customdata}<extra></extra>",
            )
        )
        zero_line(fig)
        fig.update_yaxes(title="Score moyen", range=[-1, 1])
        fig.update_xaxes(showgrid=False)
        show(style(fig, 360))

    with c2:
        st.markdown("**Répartition des avis**")
        order = op_agg["operateur_name"].tolist()[::-1]
        fig = go.Figure()
        for lab in SENTIMENT_ORDER:
            vals = op_agg.set_index("operateur_name").loc[order, lab]
            fig.add_trace(
                go.Bar(
                    y=order,
                    x=vals,
                    name=lab,
                    orientation="h",
                    marker_color=SENTIMENT_COLORS[lab],
                    text=vals.map("{:.0f}%".format),
                    textposition="inside",
                    insidetextanchor="middle",
                    hovertemplate=f"<b>%{{y}}</b><br>{lab} : %{{x:.1f}}%<extra></extra>",
                )
            )
        fig.update_layout(barmode="stack")
        fig.update_xaxes(range=[0, 100], title="Part des avis (%)", showgrid=False)
        fig.update_yaxes(showgrid=False)
        show(style(fig, 360, legend=True))

    st.dataframe(
        op_agg.rename(
            columns={
                "operateur_name": "Opérateur",
                "score_moyen": "Score moyen",
                "total_avis": "Avis",
            }
        )[["Opérateur", "Avis", "Score moyen", "Positif", "Neutre", "Négatif"]],
        hide_index=True,
        use_container_width=True,
        column_config={
            "Avis": st.column_config.NumberColumn(format="%d"),
            "Score moyen": st.column_config.NumberColumn(format="%+.2f"),
            "Positif": st.column_config.ProgressColumn("% positifs", format="%.0f%%", min_value=0, max_value=100),
            "Neutre": st.column_config.ProgressColumn("% neutres", format="%.0f%%", min_value=0, max_value=100),
            "Négatif": st.column_config.ProgressColumn("% négatifs", format="%.0f%%", min_value=0, max_value=100),
        },
    )


# ==============================================================================
# 7. ONGLET VILLES
# ==============================================================================
with tab_villes:
    section("Sentiment par ville", "Les villes sont classées par score moyen, du plus favorable au moins favorable.")

    f1, f2, f3 = st.columns([1.2, 1, 1])
    op_options = ["Tous les opérateurs"] + sorted(df_f["operateur_name"].unique().tolist())
    sel_op_city = f1.selectbox("Opérateur", op_options, key="city_op")
    min_avis = f2.slider("Avis minimum par ville", 1, 50, 5, key="city_min")
    top_n = f3.slider("Nombre de villes affichées", 5, 40, 15, key="city_n")

    src = df_f if sel_op_city == "Tous les opérateurs" else df_f[df_f["operateur_name"] == sel_op_city]
    src = src.drop_duplicates(subset=["review_id", "ville"])

    city = (
        src.groupby("ville")
        .agg(score_moyen=("sentiment_score", "mean"), total_avis=("review_id", "count"))
        .reset_index()
    )
    city = city[city["total_avis"] >= min_avis]

    if city.empty:
        empty_state(f"Aucune ville avec au moins {min_avis} avis. Réduisez le seuil.")
    else:
        # Meilleures + moins bonnes villes si trop nombreuses
        if len(city) > top_n:
            half = top_n // 2
            city = pd.concat(
                [city.nlargest(top_n - half, "score_moyen"), city.nsmallest(half, "score_moyen")]
            ).drop_duplicates("ville")
            st.caption(f"{top_n} villes affichées : les mieux et les moins bien notées.")
        city = city.sort_values("score_moyen")

        fig = go.Figure(
            go.Bar(
                x=city["score_moyen"],
                y=city["ville"],
                orientation="h",
                marker=dict(
                    color=city["score_moyen"],
                    colorscale="RdYlGn",
                    cmin=-0.6,
                    cmax=0.6,
                ),
                text=city["score_moyen"].map("{:+.2f}".format),
                textposition="outside",
                cliponaxis=False,
                customdata=city["total_avis"],
                hovertemplate="<b>%{y}</b><br>Score moyen : %{x:+.2f}<br>Avis : %{customdata}<extra></extra>",
            )
        )
        zero_line(fig, "x")
        fig.update_xaxes(range=[-1, 1], title="Score moyen")
        fig.update_yaxes(showgrid=False)
        show(style(fig, max(360, len(city) * 30)))


# ==============================================================================
# 8. ONGLET SUJETS
# ==============================================================================
with tab_sujets:
    section("Sujets abordés dans les avis", "Thèmes détectés par le modèle NLP zero-shot.")

    topic_share = (
        pd.crosstab(df_r["topic"], df_r["operateur_name"], normalize="columns") * 100
    ).reset_index().melt(id_vars="topic", var_name="Opérateur", value_name="part")

    topic_order = df_r["topic"].value_counts().index.tolist()

    c1, c2 = st.columns([1, 1.3])

    with c1:
        st.markdown("**Poids global des sujets**")
        tc = df_r["topic"].value_counts().reset_index()
        tc.columns = ["topic", "count"]
        tc["pct"] = tc["count"] / tc["count"].sum() * 100
        tc = tc.sort_values("count")
        fig = go.Figure(
            go.Bar(
                x=tc["pct"],
                y=tc["topic"],
                orientation="h",
                marker_color="#334155",
                text=tc["pct"].map("{:.0f}%".format),
                textposition="outside",
                cliponaxis=False,
                customdata=tc["count"],
                hovertemplate="<b>%{y}</b><br>%{x:.1f}% des avis (%{customdata})<extra></extra>",
            )
        )
        fig.update_xaxes(title="Part des avis (%)", showgrid=False, range=[0, tc["pct"].max() * 1.2])
        fig.update_yaxes(showgrid=False)
        show(style(fig, 400))

    with c2:
        st.markdown("**Mix de sujets par opérateur**")
        fig = px.bar(
            topic_share,
            x="topic",
            y="part",
            color="Opérateur",
            barmode="group",
            category_orders={"topic": topic_order},
            color_discrete_map={o: brand(o) for o in topic_share["Opérateur"].unique()},
        )
        fig.update_traces(hovertemplate="<b>%{fullData.name}</b><br>%{x}<br>%{y:.1f}% des avis<extra></extra>")
        fig.update_xaxes(title="", showgrid=False, tickangle=-30)
        fig.update_yaxes(title="Part des avis de l'opérateur (%)")
        show(style(fig, 400, legend=True))

    st.markdown("**Sentiment moyen par sujet et par opérateur**")
    st.markdown(
        '<div class="section-note">Vert : sujets appréciés. Rouge : sujets de mécontentement.</div>',
        unsafe_allow_html=True,
    )
    pivot = df_r.pivot_table(index="topic", columns="operateur_name", values="sentiment_score", aggfunc="mean")
    pivot = pivot.reindex(topic_order)
    fig = px.imshow(
        pivot,
        text_auto=".2f",
        color_continuous_scale="RdYlGn",
        zmin=-0.6,
        zmax=0.6,
        aspect="auto",
        labels=dict(color="Score"),
    )
    fig.update_xaxes(title="", side="top")
    fig.update_yaxes(title="")
    fig.update_coloraxes(colorbar=dict(thickness=10, len=0.8))
    show(style(fig, max(320, len(pivot) * 46)))


# ==============================================================================
# 9. ONGLET ÉVOLUTION
# ==============================================================================
with tab_temps:
    section("Évolution du sentiment", "Score moyen par période. Les périodes avec peu d'avis sont masquées pour éviter le bruit.")

    t1, t2, t3, t4 = st.columns([1.6, 1, 1, 1])
    trend_ops = t1.multiselect("Opérateurs", all_ops, default=selected_ops or all_ops, key="trend_ops")
    gran = t2.radio("Période", ["Mois", "Année"], horizontal=True)
    min_n = t3.slider("Avis min. / période", 1, 30, 5, key="trend_min")
    smooth = t4.toggle("Lissage (moyenne mobile)", value=False, disabled=(gran == "Année"))

    tcol = "mois" if gran == "Mois" else "annee"
    d = df_r[df_r["operateur_name"].isin(trend_ops)].dropna(subset=[tcol])

    trend = (
        d.groupby(["operateur_name", tcol])
        .agg(score=("sentiment_score", "mean"), n=("review_id", "count"))
        .reset_index()
        .sort_values(["operateur_name", tcol])
    )
    trend = trend[trend["n"] >= min_n]

    if trend.empty:
        empty_state(f"Aucune période avec au moins {min_n} avis. Réduisez le seuil.")
    else:
        if smooth and gran == "Mois":
            trend["score"] = trend.groupby("operateur_name")["score"].transform(
                lambda s: s.rolling(3, min_periods=1).mean()
            )

        fig = go.Figure()
        for op, g in trend.groupby("operateur_name"):
            fig.add_trace(
                go.Scatter(
                    x=g[tcol],
                    y=g["score"],
                    name=op,
                    mode="lines+markers",
                    line=dict(color=brand(op), width=2.6, shape="spline", smoothing=0.5),
                    marker=dict(size=6),
                    customdata=g["n"],
                    hovertemplate="<b>" + op + "</b><br>Score : %{y:+.2f}<br>Avis : %{customdata}<extra></extra>",
                )
            )
        zero_line(fig)
        fig.update_xaxes(title="", showgrid=False, tickformat="%b %Y" if gran == "Mois" else "%Y")
        fig.update_yaxes(title="Score moyen")
        fig.update_layout(hovermode="x unified")
        show(style(fig, 430, legend=True))


# ==============================================================================
# 10. ONGLET AVIS
# ==============================================================================
with tab_avis:
    section("Explorateur d'avis", "Consultez les avis réels et filtrez-les.")

    e1, e2, e3, e4 = st.columns([1, 1, 1, 1.4])
    f_op = e1.selectbox("Opérateur", ["Tous"] + sorted(df_r["operateur_name"].unique()), key="ex_op")
    f_topic = e2.selectbox("Sujet", ["Tous"] + sorted(df_r["topic"].unique()), key="ex_topic")
    f_sent = e3.selectbox("Sentiment", ["Tous"] + SENTIMENT_ORDER, key="ex_sent")
    kw = e4.text_input("Mot-clé", placeholder="fibre, guichet, facture…", key="ex_kw")

    ex = df_r
    if f_op != "Tous":
        ex = ex[ex["operateur_name"] == f_op]
    if f_topic != "Tous":
        ex = ex[ex["topic"] == f_topic]
    if f_sent != "Tous":
        ex = ex[ex["sentiment"] == f_sent]
    if kw:
        ex = ex[ex["Comment"].astype(str).str.contains(kw, case=False, na=False, regex=False)]

    st.caption(f"{len(ex):,} avis correspondent".replace(",", " ") + (" (100 premiers affichés)." if len(ex) > 100 else "."))

    if ex.empty:
        empty_state("Aucun avis ne correspond à ces critères.")
    else:
        view = ex.sort_values("date", ascending=False)[
            ["date", "operateur_name", "ville", "topic", "sentiment_score", "Comment"]
        ]
        st.dataframe(
            view.head(100),
            hide_index=True,
            use_container_width=True,
            height=380,
            column_config={
                "date": st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
                "operateur_name": "Opérateur",
                "ville": "Ville",
                "topic": "Sujet",
                "sentiment_score": st.column_config.NumberColumn("Score", format="%+.2f"),
                "Comment": st.column_config.TextColumn("Avis", width="large"),
            },
        )
        st.download_button(
            "Télécharger la sélection (CSV)",
            view.to_csv(index=False).encode("utf-8-sig"),
            file_name="avis_selection.csv",
            mime="text/csv",
        )

st.caption("Projet Data Engineering & Sentiment Analysis · Schéma en étoile · Télécom Maroc")