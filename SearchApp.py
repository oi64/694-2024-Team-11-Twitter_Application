##
import streamlit as st
import toml
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import euclidean_distances
import pymongo
from search import search

##
# Load the TOML file
with open('/Users/omkar/Desktop/pyCharm/Twitter_Search/.streamlit/config.toml', 'r') as f:
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
