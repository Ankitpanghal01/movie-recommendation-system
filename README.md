# CineMatch — Movie Recommendation System

A Streamlit movie discovery app using content-based filtering with TF-IDF and cosine similarity.

## Features

- Live recommendations when a movie is selected
- Dark cinematic interface
- Gradient placeholder posters generated from movie titles
- Genre chips and similarity match bars
- Surprise Me button
- Choose 5, 10, or 15 recommendations (the supplied sample has 15 movies)

## Project structure

```text
movie-recommendation-system/
├── dataset/
│   └── movies.csv
├── .streamlit/
│   └── config.toml
├── app.py
├── recommend.py
├── requirements.txt
└── README.md
```

## Setup (macOS)

From the project folder, run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

Open the local URL printed in the terminal, usually http://localhost:8501.

## Dataset columns

- `movie_id`: unique movie ID
- `title`: movie title
- `genres`: comma-separated genres
- `description`: short movie description

## How recommendations work

1. The app combines each movie's genres and description.
2. TF-IDF converts the text into feature vectors.
3. Cosine similarity compares the selected movie with the others.
4. The app displays the highest-scoring matches.

Similarity is a text-similarity score, not a probability that a viewer will like a movie.
