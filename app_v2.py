import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load dataset
df = pd.read_csv("imdb_2024_full.csv")

# Clean and convert data
df["Votes"] = df["Votes"].astype(str).str.replace(",", "").str.extract(r"(\d+)").fillna(0).astype(int)
df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce").fillna(0)

# Convert Duration to minutes
df["Duration_Minutes"] = (
    df["Duration"]
    .str.extract(r"(?:(\d+)h)?\s*(?:(\d+)m)?")
    .fillna(0)
    .astype(int)
    .apply(lambda row: row[0] * 60 + row[1], axis=1)
)

# UI settings
st.set_page_config(page_title="IMDb 2024 Movies", layout="wide")
st.title("IMDb 2024 Movies Dashboard")

# Filters
st.sidebar.header("Filter Movies")

# Duration filter
duration_filter = st.sidebar.selectbox(
    "Select Duration",
    ("All", "< 2 hrs", "2–3 hrs", "> 3 hrs")
)

if duration_filter == "< 2 hrs":
    filtered_df = df[df["Duration_Minutes"] < 120]
elif duration_filter == "2–3 hrs":
    filtered_df = df[(df["Duration_Minutes"] >= 120) & (df["Duration_Minutes"] <= 180)]
elif duration_filter == "> 3 hrs":
    filtered_df = df[df["Duration_Minutes"] > 180]
else:
    filtered_df = df.copy()

# Rating filter
rating_filter = st.sidebar.slider("Minimum Rating", min_value=0.0, max_value=10.0, value=0.0)
filtered_df = filtered_df[filtered_df["Rating"] >= rating_filter]

# Votes filter
vote_filter = st.sidebar.number_input("Minimum Votes", min_value=0, value=0)
filtered_df = filtered_df[filtered_df["Votes"] > vote_filter]

# Genre filter
unique_genres = sorted(df["Genre"].dropna().unique())
genre_filter = st.sidebar.multiselect("Select Genres", unique_genres, default=unique_genres)
filtered_df = filtered_df[filtered_df["Genre"].isin(genre_filter)]

# Filtered table
st.subheader("Filtered Movies")
st.dataframe(filtered_df.sort_values(by=["Rating", "Votes"], ascending=False).reset_index(drop=True), height=400)

# Top 10 Movies
st.subheader("Top 10 Movies by Rating and Votes")
top_movies = df.sort_values(by=["Rating", "Votes"], ascending=False).head(10)
if not top_movies.empty:
    st.bar_chart(top_movies.set_index("Title")[["Rating", "Votes"]])
else:
    st.info("No top movies found.")

# Genre Distribution
st.subheader("Genre Distribution")
genre_counts = df["Genre"].value_counts()
st.bar_chart(genre_counts)

# Average Duration by Genre
st.subheader("Average Duration by Genre")
avg_duration = df.groupby("Genre")["Duration_Minutes"].mean().sort_values()
st.bar_chart(avg_duration)

# Voting Trends by Genre
st.subheader("Average Votes by Genre")
avg_votes = df.groupby("Genre")["Votes"].mean().sort_values()
st.bar_chart(avg_votes)

# Rating Distribution
st.subheader("Rating Distribution")
fig, ax = plt.subplots()
sns.histplot(df["Rating"], bins=20, kde=True, ax=ax)
st.pyplot(fig)

# Genre-Based Rating Leaders
st.subheader("Top-Rated Movie by Genre")
top_per_genre = df.loc[df.groupby("Genre")["Rating"].idxmax()]
st.dataframe(top_per_genre[["Title", "Genre", "Rating"]])

# Most Popular Genres by Total Voting
st.subheader("Most Popular Genres by Voting (Pie Chart)")
genre_votes = df.groupby("Genre")["Votes"].sum().sort_values(ascending=False)
fig, ax = plt.subplots()
ax.pie(genre_votes, labels=genre_votes.index, autopct='%1.1f%%', startangle=140)
ax.axis("equal")
st.pyplot(fig)

# Duration Extremes
st.subheader("Duration Extremes")
shortest = df.loc[df["Duration_Minutes"].idxmin()]
longest = df.loc[df["Duration_Minutes"].idxmax()]
st.markdown("**Shortest Movie**")
st.write(shortest[["Title", "Duration", "Duration_Minutes"]])
st.markdown("**Longest Movie**")
st.write(longest[["Title", "Duration", "Duration_Minutes"]])

# Ratings by Genre - Heatmap
st.subheader("Average Ratings by Genre")
avg_rating_genre = df.groupby("Genre")["Rating"].mean().reset_index()
pivot = avg_rating_genre.pivot_table(index="Genre", values="Rating")

fig, ax = plt.subplots(figsize=(6, len(pivot) * 0.5))
sns.heatmap(pivot, annot=True, cmap="YlGnBu", ax=ax)
st.pyplot(fig)

# Correlation Analysis
st.subheader("Correlation Between Ratings and Votes")
fig, ax = plt.subplots()
sns.scatterplot(data=df, x="Rating", y="Votes", hue="Genre", ax=ax)
st.pyplot(fig)
