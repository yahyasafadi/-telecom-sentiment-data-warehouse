import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Telecom Sentiment Dashboard", layout="wide")

@st.cache_data
def load_data():
    base_path = r"C:\Users\moham\Desktop\Docker\data\dw_output"
    
    # Charger les tables
    fact = pd.read_csv(f"{base_path}\\fact_reviews.csv")
    d_op = pd.read_csv(f"{base_path}\\dim_operateur.csv")
    d_ville = pd.read_csv(f"{base_path}\\dim_ville.csv")
    d_temps = pd.read_csv(f"{base_path}\\dim_temps.csv")
    d_topic = pd.read_csv(f"{base_path}\\dim_topic.csv")
    
    # Jointures (Merge)
    df = fact.merge(d_op, on='operateur_id', how='left')
    df = df.merge(d_ville, on='ville_id', how='left')
    df = df.merge(d_temps, on='temps_id', how='left')
    df = df.merge(d_topic, on='topic_id', how='left')
    
    # Formater la date
    df['date'] = pd.to_datetime(df[['review_year', 'review_month', 'review_day']].rename(columns={'review_year':'year', 'review_month':'month', 'review_day':'day'}), errors='coerce')
    
    return df

df = load_data()

st.title("📊 Dashboard Satisfaction - Télécom Maroc")
st.markdown("Ce tableau de bord interactif analyse les sentiments des clients envers IAM, Orange et INWI.")

# --- BARRE LATÉRALE (FILTRES) ---
st.sidebar.header("Filtres")
selected_op = st.sidebar.multiselect("Opérateurs", df['operateur_name'].dropna().unique(), default=df['operateur_name'].dropna().unique())
selected_ville = st.sidebar.multiselect("Villes (Laissez vide pour tout le Maroc)", df['ville'].dropna().unique())

# Appliquer les filtres
filtered_df = df[df['operateur_name'].isin(selected_op)]
if selected_ville:
    filtered_df = filtered_df[filtered_df['ville'].isin(selected_ville)]

# --- KPIs (CARTES) ---
col1, col2 = st.columns(2)
col1.metric("Total des Avis (Sélectionnés)", len(filtered_df))
col2.metric("Score de Satisfaction Global", round(filtered_df['sentiment_score'].mean(), 2))

st.markdown("---")

# --- GRAPHIQUES ---
col_left, col_right = st.columns(2)

# 1. Évolution Temporelle
with col_left:
    st.subheader("📈 Évolution de la Satisfaction")
    # Grouper par mois et par opérateur
    df_time = filtered_df.groupby([filtered_df['date'].dt.to_period("M"), 'operateur_name'])['sentiment_score'].mean().reset_index()
    df_time['date'] = df_time['date'].dt.to_timestamp()
    fig1 = px.line(df_time, x='date', y='sentiment_score', color='operateur_name', title="Satisfaction au fil du temps")
    st.plotly_chart(fig1, width="stretch")

# 2. Comparatif Opérateurs
with col_right:
    st.subheader("🏢 Comparatif Opérateurs")
    df_op = filtered_df.groupby('operateur_name')['sentiment_score'].mean().reset_index()
    fig2 = px.bar(df_op, x='operateur_name', y='sentiment_score', color='operateur_name', title="Score Moyen par Opérateur")
    st.plotly_chart(fig2, width="stretch")

col_bot_left, col_bot_right = st.columns(2)

# 3. Analyse par Ville
with col_bot_left:
    st.subheader("🏙️ Satisfaction par Ville (Top 15)")
    df_ville = filtered_df.groupby('ville')['sentiment_score'].mean().reset_index().sort_values('sentiment_score', ascending=False).head(15)
    fig3 = px.bar(df_ville, x='sentiment_score', y='ville', orientation='h', title="Villes les plus satisfaites", color='sentiment_score', color_continuous_scale='RdYlGn')
    st.plotly_chart(fig3, width="stretch")

# 4. Analyse des Sujets
with col_bot_right:
    st.subheader("🗣️ Analyse par Sujet")
    df_topic = filtered_df[filtered_df['topic'] != 'autre'].groupby('topic')['sentiment_score'].mean().reset_index()
    fig4 = px.bar(df_topic, x='topic', y='sentiment_score', color='sentiment_score', color_continuous_scale='RdYlGn', title="Satisfaction selon le Sujet")
    st.plotly_chart(fig4, width="stretch")
