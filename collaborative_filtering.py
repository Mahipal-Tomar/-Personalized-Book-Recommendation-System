import pandas as pd
import os
from scipy.sparse import coo_matrix
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Step 1: Load the data
my_books = pd.read_csv("liked_books.csv", index_col=0)
my_books["book_id"] = my_books["book_id"].astype(str)

# Step 2: Load the book ID mapping from a CSV file
csv_book_mapping = {}
with open("book_id_map.csv", "r") as f:
    while True:
        line = f.readline()
        if not line:
            break
        csv_id, book_id = line.strip().split(",")
        csv_book_mapping[csv_id] = book_id

# Step 3: Extract the book IDs from my_books
book_set = set(my_books["book_id"])

# Step 4: Display first 5 lines of the goodreads_interactions.csv file (just for preview)
with open('goodreads_interactions.csv', 'r', encoding='utf-8') as file:
    for i in range(5):
        print(file.readline().strip())

# Step 5: Find overlap users
overlap_users = {}
with open("goodreads_interactions.csv") as f:
    while True:
        line = f.readline()
        if not line:
            break
        user_id, csv_id, _, rating, _ = line.strip().split(",")
        book_id = csv_book_mapping.get(csv_id)
        if book_id in book_set:
            if user_id not in overlap_users:
                overlap_users[user_id] = 1
            else:
                overlap_users[user_id] += 1

# Filter users based on overlap count
filtered_overlap_users = {k for k, v in overlap_users.items() if v > my_books.shape[0] / 5}

# Step 6: Collect user-book interactions for filtered users
interactions_list = []
with open("goodreads_interactions.csv") as f:
    while True:
        line = f.readline()
        if not line:
            break
        user_id, csv_id, _, rating, _ = line.strip().split(",")
        if user_id in filtered_overlap_users:
            book_id = csv_book_mapping[csv_id]
            interactions_list.append([user_id, book_id, rating])

# Step 7: Create user-book interaction matrix
interactions = pd.DataFrame(interactions_list, columns=["user_id", "book_id", "rating"])
interactions = pd.concat([my_books[["user_id", "book_id", "rating"]], interactions])

# Step 8: Preprocess data for matrix factorization
interactions["book_id"] = interactions["book_id"].astype(str)
interactions["user_id"] = interactions["user_id"].astype(str)
interactions["rating"] = pd.to_numeric(interactions["rating"])

# Encode categorical columns as integers
interactions["user_id"] = interactions["user_id"].astype("category").cat.codes
interactions["book_id"] = interactions["book_id"].astype("category").cat.codes

# Step 9: Create the sparse rating matrix
ratings_mat_coo = coo_matrix((interactions["rating"], (interactions["user_id"], interactions["book_id"])))
ratings_mat = ratings_mat_coo.tocsr()

# Step 10: Find similar users to the target user (user with id -1 in this case)
my_index = 0  # Assuming you're the first user (or adjust accordingly)
similarity = cosine_similarity(ratings_mat[my_index, :], ratings_mat).flatten()

# Find the most similar users
indices = np.argpartition(similarity, -10)[-15:]

# Extract similar users' data
similar_users = interactions[interactions["user_id"].isin(indices)].copy()
similar_users = similar_users[similar_users["user_id"] != -1]

# Step 11: Create book recommendations for similar users
book_recs = similar_users.groupby("book_id").rating.agg(['count', 'mean'])

# Step 12: Merge with book titles (assuming books_titles.json contains the book metadata)
books_titles = pd.read_json("books_titles.json")
books_titles["book_id"] = books_titles["book_id"].astype(str)
book_recs = book_recs.merge(books_titles, how="inner", on="book_id")

# Step 13: Rank the book recommendations based on count and mean rating
book_recs["adjusted_count"] = book_recs["count"] * (book_recs["count"] / book_recs["ratings"])
book_recs["score"] = book_recs["mean"] * book_recs["adjusted_count"]

# Step 14: Filter out books that the user has already liked
book_recs = book_recs[~book_recs["book_id"].isin(my_books["book_id"])]

# Step 15: Remove books based on title similarity
my_books["mod_titles"] = my_books["title"].str.replace("[^a-zA-Z0-9 ]", "", regex=True).str.lower()
my_books["mod_titles"] = my_books["title"].str.replace("\s+", " ", regex=True)
book_recs = book_recs[~book_recs["mod_title"].isin(my_books["mod_titles"])]
book_recs = book_recs[book_recs["count"] > 2]
book_recs = book_recs[book_recs["mean"] > 4]

# Step 16: Sort the recommendations by score
top_recs = book_recs.sort_values("score", ascending=False)

# Output the top recommendations
print(top_recs)

# Optionally, you can save the top recommendations to a CSV file
top_recs.to_csv("top_book_recommendations.csv")
