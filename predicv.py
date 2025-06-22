import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from statsmodels.tsa.arima.model import ARIMA
import warnings

warnings.filterwarnings("ignore")

st.set_page_config(page_title="Prédiction des Ventes", layout="centered")

st.title("📈 Prédiction des Ventes par Article")
st.markdown("Téléverse un fichier Excel contenant les ventes annuelles par article.")

# Upload du fichier Excel
uploaded_file = st.file_uploader("Choisir un fichier Excel", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        st.success("Fichier chargé avec succès !")

        # Vérification des colonnes attendues
        expected_columns = {'Année', 'Article', 'Ventes'}
        if not expected_columns.issubset(df.columns):
            st.error("Le fichier doit contenir les colonnes suivantes : Année, Article, Ventes.")
        else:
            articles = df['Article'].unique()
            article_selection = st.selectbox("Sélectionne un article à prédire :", articles)

            # Données filtrées
            df_article = df[df['Article'] == article_selection].sort_values("Année")
            df_article.set_index("Année", inplace=True)

            # Affichage de la série historique
            st.subheader("📊 Ventes historiques")
            st.line_chart(df_article["Ventes"])

            # Modélisation ARIMA
            if len(df_article) >= 4:
                model = ARIMA(df_article["Ventes"], order=(1, 1, 1))
                model_fit = model.fit()

                # Prévision
                forecast_horizon = st.slider("Nombre d'années à prédire :", 1, 5, 3)
                forecast = model_fit.forecast(steps=forecast_horizon)
                last_year = df_article.index[-1]

                # Créer un DataFrame des prévisions
                future_years = list(range(last_year + 1, last_year + forecast_horizon + 1))
                df_forecast = pd.DataFrame({
                    "Année": future_years,
                    "Article": article_selection,
                    "Ventes": forecast.values
                })

                # Fusion avec les données originales
                df_final = pd.concat([df.reset_index(), df_forecast], ignore_index=True)

                # Affichage des prévisions
                st.subheader("🔮 Prévisions")
                fig, ax = plt.subplots()
                df_plot = df_final[df_final["Article"] == article_selection]
                ax.plot(df_plot["Année"], df_plot["Ventes"], marker='o')
                ax.set_title(f"Ventes prévues pour {article_selection}")
                ax.set_xlabel("Année")
                ax.set_ylabel("Ventes")
                ax.grid()
                st.pyplot(fig)

                # Téléchargement du fichier avec prévisions
                st.subheader("📥 Télécharger le fichier avec prévisions")


                def to_excel(df):
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False, sheet_name='Prévisions')
                    return output.getvalue()


                excel_bytes = to_excel(df_final)

                st.download_button(
                    label="📤 Télécharger le fichier Excel",
                    data=excel_bytes,
                    file_name="previsions_ventes.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.warning("Pas assez de données pour faire une prévision fiable (minimum 4 années).")
    except Exception as e:
        st.error(f"Erreur lors de la lecture du fichier : {e}")