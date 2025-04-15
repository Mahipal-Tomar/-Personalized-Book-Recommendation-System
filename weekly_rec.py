import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

# Load interactions and book titles data
interactions = pd.read_csv("goodreads_interactions.csv")
books_titles = pd.read_json("books_titles.json")

# Convert book_id to string to match formats
books_titles['book_id'] = books_titles['book_id'].astype(str)

# Convert interaction date to datetime format
interactions['date'] = pd.to_datetime(interactions['date'])

# Function to get popular books within a specific date range
def get_popular_books(interactions, days=7, min_rating=4):
    date_threshold = datetime.now() - timedelta(days=days)
    
    # Filter interactions by date and rating
    recent_interactions = interactions[interactions['date'] >= date_threshold]
    high_rated = recent_interactions[recent_interactions['rating'].astype(float) >= min_rating]
    
    # Count ratings per book
    popular_books = high_rated['book_id'].value_counts().head(10)
    
    # Merge with book titles for more info
    popular_books_info = books_titles[books_titles['book_id'].isin(popular_books.index)]
    return popular_books_info

# Get popular books for the past week and month
popular_weekly_books = get_popular_books(interactions, days=7)
popular_monthly_books = get_popular_books(interactions, days=30)
