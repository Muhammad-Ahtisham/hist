import streamlit as st
import pandas as pd
import sqlite3
import os
DB_FILE = "recommendation.db"
st.set_page_config(page_title="Medical Tool Recommendation", layout="centered")
st.title("🔬 Medical Tool Recommendation System")

# Upload fallback if database not found
if not os.path.exists(DB_FILE):
    st.warning("Database not found. Please upload `recommendation.db`.")
    uploaded_file = st.file_uploader("Upload SQLite DB", type="db")
    if uploaded_file:
        with open(DB_FILE, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success("Database uploaded! Please reload the page.")
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

def add_user(user_data):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO users (
                userID, userCategory, location, experienceLevel, previousPurchases, 
                lastPurchaseDate, preferredBrand, specialization, budgetRange
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, user_data)
        conn.commit()
        st.success(f"User '{user_data[0]}' added successfully!")
        st.cache_data.clear()
    except sqlite3.IntegrityError:
        st.error(f"User ID '{user_data[0]}' already exists.")
    finally:
        conn.close()

def recommend_tools(user_id):
    users_df = load_users()
    tools_df = load_tools()
    user = users_df[users_df["userID"] == user_id]
    if user.empty:
        return []
    purchased = user.iloc[0]["previousPurchases"].split("|") if user.iloc[0]["previousPurchases"] else []
    recommendations = tools_df[~tools_df["Title"].isin(purchased)]
    return recommendations

# --- UI Layout ---
tab1, tab2, tab3 = st.tabs(["📊 View Data", "✨ Recommend", "➕ Add User"])

with tab1:
    st.subheader("👤 Users Table")
    st.dataframe(load_users())

    st.subheader("🧰 Tools Table")
    st.dataframe(load_tools()[["Title", "Category", "Price", "Type"]])

with tab2:
    st.subheader("🔎 Tool Recommendations")
    users = load_users()
    user_ids = users["userID"].tolist()

    selected_user = st.selectbox("Select User ID:", user_ids)
    if selected_user:
        recs = recommend_tools(selected_user)
        if not recs.empty:
            st.markdown("### Recommended Tools:")
            for _, row in recs.iterrows():
                st.markdown(f"""
                **{row['Title']}**  
                Category: {row['Category']} | Type: {row['Type']} | Price: {row['Price']}  
                [View Tool]({row['Title_URL']})  
                """)
        else:
            st.info("User has purchased all tools!")

with tab3:
    st.subheader("➕ Add New User")

    with st.form("add_user_form"):
        user_id = st.text_input("User ID")
        category = st.text_input("User Category")
        location = st.text_input("Location")
        experience = st.selectbox("Experience Level", ["Beginner", "Intermediate", "Expert"])
        tools = st.multiselect("Previous Purchases", load_tools()["Title"].tolist())
        purchase_date = st.date_input("Last Purchase Date")
        brand = st.text_input("Preferred Brand")
        specialization = st.text_input("Specialization")
        budget = st.text_input("Budget Range")

        submitted = st.form_submit_button("Add User")

        if submitted:
            if not user_id or not tools:
                st.error("User ID and purchases are required.")
            else:
                user_data = (
                    user_id, category, location, experience, "|".join(tools),
                    str(purchase_date), brand, specialization, budget
                )
                add_user(user_data)
