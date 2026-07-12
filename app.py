import streamlit as st
import pickle
import requests
import os
from dotenv import load_dotenv


# ---------------- TMDB API KEY ----------------
load_dotenv()

API_KEY = os.getenv("TMDB_API_KEY")
# ---------------- LOAD DATA ----------------
movies = pickle.load(open("movies.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))

# ---------------- FETCH POSTER ----------------
session = requests.Session()

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{int(movie_id)}"

    try:
        response = session.get(
            url,
            params={
                "api_key": API_KEY,
                "language": "en-US"
            },
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        if response.status_code == 200:
            data = response.json()

            if data.get("poster_path"):
                return (
                    "https://image.tmdb.org/t/p/w500"
                    + data["poster_path"]
                )

        print("TMDB Error:", response.status_code)

    except Exception as e:
        print("Poster Error:", e)

    # Placeholder image if request fails
    return "https://via.placeholder.com/300x450?text=No+Poster"

# ---------------- RECOMMEND ----------------
def recommend(movie):

    movie_index = movies[movies["title"] == movie].index[0]

    distances = similarity[movie_index]

    movie_list = sorted(
        list(enumerate(distances)),
        key=lambda x: x[1],
        reverse=True
    )[1:6]

    recommended_movies = []
    recommended_posters = []

    for i in movie_list:

        movie_id = movies.iloc[i[0]]["movie_id"]

        recommended_movies.append(
            movies.iloc[i[0]]["title"]
        )

        recommended_posters.append(
            fetch_poster(movie_id)
        )

    return recommended_movies, recommended_posters

# ---------------- STREAMLIT ----------------
st.set_page_config(
    page_title="Movie Recommendation System",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 Movie Recommendation System")

selected_movie = st.selectbox(
    "Select a Movie",
    movies["title"].values
)

if st.button("Recommend"):

    names, posters = recommend(selected_movie)

    cols = st.columns(5)

    for i in range(5):
        with cols[i]:
            st.image(posters[i], width=180)
            st.markdown(
                f"**{names[i]}**"
            )