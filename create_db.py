import pandas as pd
import sqlite3

# Load Excel files
tools_df = pd.read_excel("Tools_2.xlsx")
users_df = pd.read_excel("surgical_tool_recommendation_users.xlsx")

# Connect to SQLite
conn = sqlite3.connect("recommendation.db")
cursor = conn.cursor()

# Drop old tables if they exist
cursor.execute("DROP TABLE IF EXISTS tools")
cursor.execute("DROP TABLE IF EXISTS users")

# Create tools table
cursor.execute('''
CREATE TABLE tools (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Title TEXT,
    Title_URL TEXT,
    Image TEXT,
    onsale TEXT,
    add_to_wishlist_URL TEXT,
    add_to_wishlist TEXT,
    View TEXT,
    Category TEXT,
    Price TEXT,
    Price1 TEXT,
    Type_URL TEXT,
    Type TEXT
)
''')

# Create users table
cursor.execute('''
CREATE TABLE users (
    userID TEXT PRIMARY KEY,
    userCategory TEXT,
    location TEXT,
    experienceLevel TEXT,
    previousPurchases TEXT,
    lastPurchaseDate TEXT,
    preferredBrand TEXT,
    specialization TEXT,
    budgetRange TEXT
)
''')

# Insert data
tools_df.to_sql("tools", conn, if_exists="append", index=False)
users_df.to_sql("users", conn, if_exists="append", index=False)

conn.commit()
conn.close()
print("recommendation.db created successfully.")
