import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
from state_manager import get_liked_books, get_liked_books_data,initialize_state
import search
import recommend
from datetime import datetime, timedelta

def filter_books(query):
    query = query.lower()
    return search.search_book(query,search.vectorizer)

initialize_state()

def display_books(filtered_df_name):
    num_columns = 3 

    for i in range(0, len(filtered_df_name), num_columns):
        cols = st.columns(num_columns) 

        for j, col in enumerate(cols):
            if i + j < len(filtered_df_name):
                row = filtered_df_name.iloc[i + j]
                with col:
                    st.image(row['cover_image'], width=200)
                    st.markdown(f"**{row['title']}**") 
                    st.text(f"Ratings: {row['ratings']}") 
                    st.markdown(f"[More details]({row['url']})", unsafe_allow_html=True)

                    # Button to like the book
                    if st.button(f"Like {row['title']}", key=f"like_button_{row['book_id']}"):
                        if row['book_id'] not in st.session_state.liked_books:
                            st.session_state.liked_books.append(row['book_id'])
                            st.session_state.liked_books_data.append(row.to_dict())
                            st.success(f"Liked {row['title']}")

                    st.write("")

st.title('Book Recommendation System')

# Navigation
with st.sidebar:
    selected = option_menu(
        menu_title="Menu",  # Required
        options=["Home", "Search", "Recommendations", "Liked Books", "About"],
        icons=["house", "search", "book", "heart", "info-circle"],
        menu_icon="cast", 
        default_index=0, 
        styles={
            "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#F0F0F0aa"},
            "nav-link-selected": {"background-color": "#4CAF50"}
        }
    )

if selected == "Home":
    st.write("This is the home page where you can find an overview of the app and its features.")

if selected == "Search":
    search_query_name = st.text_input("Enter book name:")
    
    # Store the search query in session state to persist across reruns
    if 'search_query_name' not in st.session_state:
        st.session_state.search_query_name = ''

    search_button_name = st.button("Search")
    
    # Update the search query in session state when the button is clicked
    if search_button_name:
        st.session_state.search_query_name = search_query_name

    filtered_df_name = filter_books(st.session_state.search_query_name)
    # Use the search query from session state to filter the dataframe
    #filtered_df_name = df[df['title'].str.contains(st.session_state.search_query_name, case=False, na=False)]

    if st.session_state.search_query_name and filtered_df_name.empty:
        st.write("No books found. Please try a different search term.")
    elif st.session_state.search_query_name:
        display_books(filtered_df_name)

# Display the liked books

elif selected == "Recommendations":
   st.write("Books for you-")
   display_books(recommend.recommend_book(st.session_state.liked_books))

elif selected == "Liked Books":
    st.write("Liked Books")
    liked_books_df = pd.DataFrame(st.session_state.liked_books_data)
    display_books(liked_books_df)

elif selected == "About":
    st.write("This app is built with Streamlit to recommend books based on your interests and searches.")


    

from datetime import datetime, timedelta

# Load the interactions and book titles data
@st.cache_data
def load_data():
    interactions = pd.read_csv("goodreads_interactions.csv")
    books_titles = pd.read_json("books_titles.json")
    return interactions, books_titles

# Load the data
interactions, books_titles = load_data()

# Convert book_id to string to match formats
books_titles['book_id'] = books_titles['book_id'].astype(str)

# Convert interaction date to datetime format
interactions['date'] = pd.to_datetime(interactions['date'])

# Function to get popular books within a specific date range
def get_popular_books(interactions, books_titles, days=7, min_rating=4):
    date_threshold = datetime.now() - timedelta(days=days)
    
    # Filter interactions by date and rating
    recent_interactions = interactions[interactions['date'] >= date_threshold]
    high_rated = recent_interactions[recent_interactions['rating'].astype(float) >= min_rating]
    
    # Count ratings per book
    popular_books = high_rated['book_id'].value_counts().head(10)
    
    # Merge with book titles for more info
    popular_books_info = books_titles[books_titles['book_id'].isin(popular_books.index)]
    return popular_books_info

# Function to make clickable Goodreads link
def make_clickable(url):
    return f'<a href="{url}" target="_blank">Goodreads Link</a>'

# Function to show book cover image
def show_image(url):
    return f'<img src="{url}" width="50">'

# Function to render books in a Streamlit-friendly format
def display_books(books_info):
    # Create clickable URLs and images
    books_info['Goodreads'] = books_info['url'].apply(make_clickable)
    books_info['Cover'] = books_info['cover_image'].apply(show_image)
    
    # Display table with cover image, title, and link
    st.markdown(books_info[['title', 'Goodreads', 'Cover']].to_html(escape=False), unsafe_allow_html=True)

# Streamlit interface
st.title("Book Recommendation System")

# Get popular books for the past week and month
popular_weekly_books = get_popular_books(interactions, books_titles, days=7)
popular_monthly_books = get_popular_books(interactions, books_titles, days=30)

# Display popular books
st.subheader("Popular Books of the Week")
display_books(popular_weekly_books)

st.subheader("Popular Books of the Month")
display_books(popular_monthly_books)

# Optional: Customize time ranges
days = st.slider("Select the time range in days", min_value=1, max_value=365, value=30)
popular_custom_books = get_popular_books(interactions, books_titles, days=days)
st.subheader(f"Popular Books of the Last {days} Days")
display_books(popular_custom_books)



