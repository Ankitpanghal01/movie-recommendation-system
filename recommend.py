import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class MovieRecommender:

    def __init__(self, dataset_path):
        self.movies = pd.read_csv(dataset_path)

        self.movies["genres"] = self.movies["genres"].fillna("")
        self.movies["description"] = self.movies["description"].fillna("")

        self.movies["combined_features"] = (
            self.movies["genres"] + " " +
            self.movies["description"]
        )

        self.vectorizer = TfidfVectorizer(stop_words="english")

        self.movie_vectors = self.vectorizer.fit_transform(
            self.movies["combined_features"]
        )

        self.similarity = cosine_similarity(self.movie_vectors)

    def recommend(self, movie_title, top_n=5):

        matches = self.movies[
            self.movies["title"].str.lower() == movie_title.lower()
        ]

        if matches.empty:
            return pd.DataFrame()

        movie_index = matches.index[0]

        scores = list(enumerate(self.similarity[movie_index]))

        scores = sorted(scores, key=lambda x: x[1], reverse=True)

        scores = [item for item in scores if item[0] != movie_index]

        top_movies = scores[:top_n]

        indices = [item[0] for item in top_movies]

        recommendations = self.movies.iloc[indices][
            ["movie_id", "title", "genres", "description"]
        ].copy()

        recommendations["similarity_score"] = [
            round(item[1] * 100, 2) for item in top_movies
        ]

        return recommendations