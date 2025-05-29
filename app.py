import streamlit as st
import pandas as pd
import sqlite3
import os

DB_FILE = "recommendation.db"

st.set_page_config(page_title="Medical Tool Recommender", layout="centered")

st.title("🔬 Medical Tool Recommendation App")
st.write("This app displays user data from the `recommendation.db` SQLite database.")

# --- Upload database if not found ---
if not os.path.exists(DB_FILE):
    st.warning("Database file not found. Please upload your 'recommendation.db' SQLite file.")
    uploaded_file = st.file_uploader("Upload recommendation.db", type=["db"])
    if uploaded_file:
        with open(DB_FILE, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success("Database uploaded successfully! Please reload.")
        st.stop()
    else:
        st.stop()

# --- Load Data ---
@st.cache_data
def load_user_data():
    try:
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql("SELECT * FROM users", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error loading user data: {e}")
        return pd.DataFrame()

@st.cache_data
def load_tool_data():
    try:
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql("SELECT * FROM tools", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error loading tools data: {e}")
        return pd.DataFrame()

# --- Display Data ---
st.subheader("👤 Users Table")
user_df = load_user_data()
if not user_df.empty:
    st.dataframe(user_df)
else:
    st.warning("No data found in the `users` table.")

st.subheader("🧰 Tools Table")
tools_df = load_tool_data()
if not tools_df.empty:
    st.dataframe(tools_df)
else:
    st.warning("No data found in the `tools` table.")
