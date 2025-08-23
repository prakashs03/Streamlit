import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3

# -------------------------------
# Load Data from SQL Database
# -------------------------------
@st.cache_data
def load_data():
    conn = sqlite3.connect("imdb2024.db")  # your DB file
    df = pd.read_sql("SELECT * FROM movies", conn)
    conn.close()

    # Convert columns to proper types
    df["Votes"] = (
        df["Votes"]
        .astype(str)
        .str.replace(",", "")
        .str.replace("(", "")
        .str.replace(")", "")
        .str.replace("K", "000")
        .str.strip()
        .fillna("0")
        .astype(int)
    )
    df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce")
    df["Duration"] = pd.to_numeric(df["Duration"], errors="coerce")
    df["Genre"] = df["Genre"].astype(str)

    return df


df = load_data()

# -------------------------------
# Sidebar Filters
# -------------------------------
st.sidebar.header("Filter Options")

# Genre filter (multi or single)
all_genres = sorted(df["Genre"].unique())
selected_genres = st.sidebar.multiselect("Select Genres", all_genres, default=all_genres)

# Duration filter
duration_filter = st.sidebar.radio(
    "Select Duration Range (hrs)", ["All", "< 2 hrs", "2–3 hrs", "> 3 hrs"]
)

# Rating filter
rating_filter = st.sidebar.slider("Minimum Rating", 0.0, 10.0, 0.0, 0.1)

# Votes filter
vote_filter = st.sidebar.number_input("Minimum Votes", min_value=0, value=0, step=1000)

# -------------------------------
# Apply Filters
# -------------------------------
filtered_df = df.copy()

# Genre filter
if selected_genres:
    filtered_df = filtered_df[filtered_df["Genre"].isin(selected_genres)]

# Duration filter
if duration_filter == "< 2 hrs":
    filtered_df = filtered_df[filtered_df["Duration"] < 120]
elif duration_filter == "2–3 hrs":
    filtered_df = filtered_df[(filtered_df["Duration"] >= 120) & (filtered_df["Duration"] <= 180)]
elif duration_filter == "> 3 hrs":
    filtered_df = filtered_df[filtered_df["Duration"] > 180]

# Rating filter
filtered_df = filtered_df[filtered_df["Rating"] >= rating_filter]

# Votes filter
filtered_df = filtered_df[filtered_df["Votes"] >= vote_filter]

# -------------------------------
# Dashboard Title
# -------------------------------
st.title("🎬 IMDb 2024 Movies Dashboard")

st.subheader("📊 Filtered Movies")
st.dataframe(filtered_df.sort_values(by="Rating", ascending=False))

# -------------------------------
# Visualizations
# -------------------------------
st.subheader("Top 10 Movies by Rating & Votes")
top_movies = (
    filtered_df.sort_values(by=["Rating", "Votes"], ascending=[False, False])
    .head(10)
)
if not top_movies.empty:
    fig1 = px.bar(
        top_movies,
        x="Title",
        y=["Rating", "Votes"],
        barmode="group",
        title="Top 10 Movies",
    )
    st.plotly_chart(fig1, use_container_width=True)
else:
    st.info("No movies match the selected filters.")

st.subheader("Genre Distribution")
genre_count = filtered_df["Genre"].value_counts().reset_index()
genre_count.columns = ["Genre", "Count"]
fig2 = px.bar(genre_count, x="Genre", y="Count", title="Movies by Genre")
st.plotly_chart(fig2, use_container_width=True)

st.subheader("Most Popular Genres by Voting")
genre_votes = (
    filtered_df.groupby("Genre")["Votes"].sum().reset_index().sort_values("Votes", ascending=False)
)
if not genre_votes.empty:
    fig3 = px.pie(genre_votes, names="Genre", values="Votes", title="Genres by Total Votes", hole=0.3)
    fig3.update_layout(height=500)  # enlarge pie chart
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("No data available for pie chart.")

st.subheader("Rating Distribution")
fig4 = px.histogram(filtered_df, x="Rating", nbins=20, title="Ratings Histogram")
st.plotly_chart(fig4, use_container_width=True)

st.subheader("Correlation: Rating vs Votes")
fig5 = px.scatter(
    filtered_df,
    x="Votes",
    y="Rating",
    color="Genre",
    size="Votes",
    hover_data=["Title"],
    title="Ratings vs Votes",
)
st.plotly_chart(fig5, use_container_width=True)

# -------------------------------
# Duration Extremes
# -------------------------------
st.subheader("Shortest & Longest Movies")
if not filtered_df.empty:
    shortest = filtered_df.loc[filtered_df["Duration"].idxmin()]
    longest = filtered_df.loc[filtered_df["Duration"].idxmax()]

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Shortest Movie", f"{shortest['Title']}", f"{shortest['Duration']} mins")
    with col2:
        st.metric("Longest Movie", f"{longest['Title']}", f"{longest['Duration']} mins")
