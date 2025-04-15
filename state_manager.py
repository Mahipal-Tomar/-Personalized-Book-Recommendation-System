import streamlit as st

def initialize_state():
    if 'liked_books' not in st.session_state:
        st.session_state.liked_books = []

    if 'liked_books_data' not in st.session_state:
        st.session_state.liked_books_data = []

def get_liked_books():
    initialize_state()
    return st.session_state.liked_books

def get_liked_books_data():
    initialize_state()
    return st.session_state.liked_books_data