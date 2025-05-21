import streamlit as st
import requests
import pandas as pd
import json

st.set_page_config(page_title="DataLake-API Tester", layout="wide")
st.title("DataLake-API – Test Automatique")

API_URL = "http://127.0.0.1:8000/api"

# -- Gestion de session utilisateur -- #
if "token" not in st.session_state:
    st.session_state["token"] = None

# -- AUTHENTIFICATION -- #
st.sidebar.header("Authentification")

if st.session_state["token"]:
    st.sidebar.success("Connecté")
    if st.sidebar.button("Se déconnecter"):
        st.session_state["token"] = None
        #st.experimental_rerun()
else:
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Se connecter"):
        auth_response = requests.post(f"{API_URL}/token/", json={"username": username, "password": password})
        if auth_response.status_code == 200:
            st.session_state["token"] = auth_response.json()["access"]
            st.sidebar.success("Connecté avec succès")
            #st.experimental_rerun()
        else:
            st.sidebar.error("Échec d'authentification")

# -- Protection des onglets si non connecté -- #
if not st.session_state["token"]:
    st.warning("Vous devez être connecté pour accéder aux fonctionnalités.")
    st.stop()

headers = {"Authorization": f"Bearer {st.session_state['token']}"}

# -- TABS PRINCIPAUX -- #
tabs = st.tabs(["Dataset", "Transactions", "Métriques", "Recherche", "Audit", "Lineage", "Repush", "ML"])

# -- DATASET -- #
with tabs[0]:
    st.subheader("Aperçu du Dataset")
    all_fields = ["customer_name", "country", "status", "amount", "payment_method", "order_date", "segment", "product_name"]
    selected_fields = st.multiselect(
        "Champs à afficher :",
        all_fields,
        default=["customer_name", "country", "status", "amount"]
    )
    if st.button("Charger l'intégralité du dataset"):
        params = {
            "fields": ",".join(selected_fields),
            "all": "true"
        }
        r = requests.get(f"{API_URL}/transactions/", headers=headers, params=params)
        if r.status_code == 200:
            data = r.json()
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
            st.download_button("Télécharger en CSV", data=df.to_csv(index=False), file_name="transactions.csv")
        else:
            st.error(f"Erreur {r.status_code} : {r.text}")

# -- TRANSACTIONS -- #
with tabs[1]:
    st.subheader("Transactions avec filtres")
    country = st.text_input("Filtrer par pays")
    payment = st.text_input("Filtrer par méthode de paiement")
    fields = st.text_input("Projection des champs (ex: customer_name,amount)")

    params = {}
    if country:
        params["country"] = country
    if payment:
        params["payment_method"] = payment
    if fields:
        params["fields"] = fields

    if st.button("Récupérer les transactions"):
        r = requests.get(f"{API_URL}/transactions/", headers=headers, params=params)
        if r.status_code == 200:
            data = r.json().get("results", r.json())
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
        else:
            st.error(f"Erreur {r.status_code} : {r.text}")

# -- METRICS -- #
with tabs[2]:
    st.subheader("Métriques disponibles")
    endpoints = [
        "avg-spend", "avg-rating", "sales-per-country",
        "rating-distribution", "daily-activity", "busiest-day",
        "recent-spend", "total-per-user", "top-products"
    ]
    choice = st.selectbox("Choisir une métrique", endpoints)
    x = st.number_input("Top X (si applicable)", min_value=1, value=5) if "top" in choice else None
    if st.button("Calculer la métrique"):
        url = f"{API_URL}/metrics/{choice}/"
        if x:
            url += f"?x={x}"
        r = requests.get(url, headers=headers)
        st.json(r.json())

# -- SEARCH -- #
with tabs[3]:
    st.subheader("Recherche full-text")
    q = st.text_input("Mot-clé")
    if st.button("Rechercher"):
        r = requests.get(f"{API_URL}/search/", headers=headers, params={"q": q})
        st.json(r.json())

# -- AUDIT -- #
with tabs[4]:
    st.subheader("Audit log")
    if st.button("Afficher les 100 derniers appels"):
        r = requests.get(f"{API_URL}/audit/", headers=headers)
        df = pd.DataFrame(r.json())
        st.dataframe(df, use_container_width=True)

# -- LINEAGE -- #
with tabs[5]:
    st.subheader("Lineage (traçabilité d'une transaction)")
    tx_id = st.number_input("ID de transaction", min_value=1)
    if st.button("Voir qui a accédé à cette transaction"):
        r = requests.get(f"{API_URL}/lineage/{int(tx_id)}/", headers=headers)
        st.json(r.json())

# -- REPUSH -- #
with tabs[6]:
    st.subheader("Re-push Kafka")
    rid = st.number_input("ID transaction à repusher", min_value=1, key="repush")
    if st.button("Repush"):
        r = requests.post(f"{API_URL}/repush/{int(rid)}/", headers=headers)
        st.json(r.json())

# -- ML -- #
with tabs[7]:
    st.subheader("Entraînement ML")
    if st.button("Lancer le modèle ML"):
        r = requests.post(f"{API_URL}/train-ml/", headers=headers)
        st.json(r.json())
