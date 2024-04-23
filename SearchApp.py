##
import streamlit as st
import toml
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import euclidean_distances
import pymongo
from search import search
import os

##
cwd = os.getcwd()
print(cwd)
# Load the TOML file
with open(f'{cwd}/.streamlit/config.toml', 'r') as f:
    config = toml.load(f)

# Get the color settings from the TOML file
primaryColor = config['theme']['primaryColor']
backgroundColor = config['theme']['backgroundColor']
secondaryBackgroundColor = config['theme']['secondaryBackgroundColor']
textColor = config['theme']['textColor']

# Set the theme of the Streamlit app
st.markdown(
    f"""
    <style>
        .stApp {{
            background-color: {backgroundColor};
            color: {textColor};
        }}
    </style>
    """,
    unsafe_allow_html=True
)
##
# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")

# Create a new database
db = client["twitter"]

# Create a new collection
collection = db["tweet_cluster_centroids"]


top_5_tweets = search("Trump")
print(top_5_tweets)

def search(input_keyword):
    model = SentenceTransformer('all-mpnet-base-v2')
    vector_of_input_keyword = model.encode(input_keyword)

    # Find the closest cluster to the input vector
    closest_cluster = None
    min_distance = float('inf')
    for i in range(7):  # Assuming 7 clusters tweet_cluster_0 to tweet_cluster_6
        centroid_doc = collection.find_one({"_id": f"cluster_{i}"})
        centroid = centroid_doc["centroid"]
        distance = euclidean_distances([vector_of_input_keyword], [centroid])[0][0]
        if distance < min_distance:
            min_distance = distance
            closest_cluster = i

    closest_cluster_collection = db[f"tweet_cluster_{closest_cluster}"]
    tweets_in_cluster = closest_cluster_collection.find()
    tweet_vectors = [tweet["text_embeddings"] for tweet in tweets_in_cluster]

    # Calculate L2 norm distances
    distances = euclidean_distances([vector_of_input_keyword], tweet_vectors)[0]

    # Get indices of top 5 tweets
    top_5_indices = distances.argsort()[:5]

    # Retrieve top 5 tweets
    tweets_in_cluster = closest_cluster_collection.find()
    all_tweets = [[_tweet["user"],_tweet["text"]] for _tweet in tweets_in_cluster]
    top_5_tweets = [all_tweets[i] for i in top_5_indices]

    return top_5_tweets

##
def main():
    st.title("Search Tweets")

    # Input: User enters search query
    search_query = st.text_input("Enter your search query")

    # Button: User triggers the search
    if st.button("Search"):
        if search_query:
            # Perform the search and get results
            results = search(search_query)

            # Display search results
            st.subheader("Search Results")
            for result in results:
                with st.container():
                    if result :
                        try:
                            st.header(f"{result[0]}")
                        except Exception as e:
                            print(e)

                        try:
                            st.write(f"Tweet: {result[1]}")
                        except Exception as e:
                            print(e)
                        st.divider()


if __name__ == "__main__":
    main()
