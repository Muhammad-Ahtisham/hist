import streamlit as st
import pandas as pd
import sqlite3
import os

DB_FILE = "recommendation.db"

st.set_page_config(page_title="🔬 Medical Tool Recommendation App", layout="centered")

st.title("🔬 Medical Tool Recommendation App")

# Upload DB if not present
if not os.path.exists(DB_FILE):
    st.warning("Database file not found. Please upload your 'recommendation.db' SQLite file.")
    uploaded_file = st.file_uploader("Upload recommendation.db", type=["db"])
    if uploaded_file:
        with open(DB_FILE, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success("Database uploaded. Please reload the page.")
        st.stop()
    else:
        st.stop()

# Loaders
@st.cache_data
def load_users():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql("SELECT * FROM users", conn)
    conn.close()
    return df

@st.cache_data
def load_tools():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql("SELECT * FROM tools", conn)
    conn.close()
    return df

def add_user(user_id, purchases):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (userID, previousPurchases) VALUES (?, ?)", (user_id, purchases))
        conn.commit()
        conn.close()
        st.success(f"User '{user_id}' added successfully!")
        st.cache_data.clear()
    except sqlite3.IntegrityError:
        st.error(f"User ID '{user_id}' already exists. Please choose another.")

# Recommend tools the user hasn't purchased
def recommend_tools(user_id):
    users_df = load_users()
    tools_df = load_tools()
    
    user_row = users_df[users_df['userID'] == user_id]
    if user_row.empty:
        return []
    
    purchased = user_row.iloc[0]['previousPurchases'].split('|')
    all_tools = tools_df['Title'].tolist()
    recommendations = [tool for tool in all_tools if tool not in purchased]
    return recommendations

# --- Main App ---
tab1, tab2, tab3 = st.tabs(["📋 View Data", "✨ Recommend Tools", "➕ Add New User"])

with tab1:
    st.subheader("👤 Users Table")
    st.dataframe(load_users())

    st.subheader("🧰 Tools Table")
    st.dataframe(load_tools())

with tab2:
    st.subheader("✨ Tool Recommendations")
    users_df = load_users()
    user_ids = users_df['userID'].tolist()
    
    selected_user = st.selectbox("Select a user ID:", user_ids)
    if selected_user:
        recs = recommend_tools(selected_user)
        if recs:
            st.markdown("#### Recommended Tools:")
            for r in recs:
                st.write(f"• {r}")
        else:
            st.info("All available tools already purchased!")

with tab3:
    st.subheader("➕ Add a New User")

    with st.form("user_form"):
        new_user_id = st.text_input("User ID")
        all_tool_titles = load_tools()['Title'].tolist()
        selected_tools = st.multiselect("Select Purchased Tools", options=all_tool_titles)

        submitted = st.form_submit_button("Add User")
        if submitted:
            if new_user_id.strip() == "" or not selected_tools:
                st.error("User ID and at least one purchase are required.")
            else:
                purchases_str = "|".join(selected_tools)
                add_user(new_user_id, purchases_str)
