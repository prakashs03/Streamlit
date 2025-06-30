import streamlit as st
import sqlite3
import pandas as pd

# Page settings
st.set_page_config(page_title="IMDb SQL Query Interface", layout="wide")

st.title("🎬 IMDb 2024 - SQL Query Explorer")

# Connect to SQLite DB
DB_PATH = "imdb2024.db"  # Ensure this file exists in the same directory
try:
    conn = sqlite3.connect(DB_PATH)
except Exception as e:
    st.error(f"Failed to connect to the database: {e}")
    st.stop()

st.markdown("Write your custom SQL queries below to explore the IMDb 2024 movie database.")

# Example queries to help users
sample_queries = {
    "All Movies": "SELECT * FROM movies LIMIT 10;",
    "Top Rated Movies": "SELECT Title, Rating FROM movies ORDER BY Rating DESC LIMIT 10;",
    "Most Voted": "SELECT Title, Votes FROM movies ORDER BY Votes DESC LIMIT 10;",
    "Action Movies > 8 Rating": "SELECT * FROM movies WHERE Genre LIKE '%Action%' AND Rating > 8.0;"
}

# Sidebar with sample query dropdown
selected_query = st.sidebar.selectbox("🔍 Try a sample query:", list(sample_queries.keys()))
query_input = st.text_area("🧠 Enter your SQL query here:", sample_queries[selected_query], height=150)

# Run the query
if st.button("Execute Query"):
    try:
        df = pd.read_sql_query(query_input, conn)
        if df.empty:
            st.warning("Query executed, but returned no results.")
        else:
            st.success("✅ Query executed successfully.")
            st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"⚠️ Query failed: {e}")

# Close DB connection when done
conn.close()
