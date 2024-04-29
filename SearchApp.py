##
import streamlit as st
import toml
import pymongo
import os
from popularity import return_top_5
from cache import cache, start_background_task, update_cache
import time
from popular_users import search_users_by_keyword, find_hashtags_by_keyword, find_top_10_users, find_top_hashtags
from cache import cache



##
cwd = os.getcwd()

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



# def search(input_keyword, n_clusters = 15):
#     model = SentenceTransformer('all-mpnet-base-v2')
#     vector_of_input_keyword = model.encode(input_keyword)

#     # Find the closest cluster to the input vector
#     closest_cluster = None
#     min_distance = float('inf')
#     for i in range(n_clusters):  # Assuming 7 clusters tweet_cluster_0 to tweet_cluster_6
#         centroid_doc = collection.find_one({"_id": f"cluster_{i}"})
#         centroid = centroid_doc["centroid"]
#         distance = euclidean_distances([vector_of_input_keyword], [centroid])[0][0]
#         if distance < min_distance:
#             min_distance = distance
#             closest_cluster = i
#     top_5_tweets = rankTweets(vector_of_input_keyword, closest_cluster)
    
#     return top_5_tweets

##
def main():

    start_background_task()

    tabs = ["Search", "Trending"]
    tab = st.sidebar.radio("Select Tab", tabs)

    if tab == "Search":
        st.title("Search Tweets")



        # Input: User enters search query
        search_query = st.text_input("Enter your search query")

        # Button: User triggers the search
        if st.button("Search"):
            start_time = time.time()
            if search_query:
                found = False
                # Perform the search and get results
                if search_query in cache:
                    found = True
                    results_tweets = cache[search_query]['Tweets']
                    results_users = cache[search_query]['Users']
                    results_hashtags = cache[search_query]['Hashtags']
                else:
                    results_tweets = return_top_5(search_query, collection)
                    results_users = search_users_by_keyword(search_query)
                    results_hashtags = find_hashtags_by_keyword(keyword=search_query)


                print(f'Time:  {(time.time() - start_time)/10} + {search_query}')


                # Display search results
                st.subheader("Search Results")

                st.header('Users')
                for result in results_users:
                    with st.container():
                        if result :
                            try:
                                st.write(f"User: {result[0]}")
                            except Exception as e:
                                print(e)

                            try:
                                st.write(f"User Name: {result[1]}")
                            except Exception as e:
                                print(e)

                            try:
                                st.write(f"Description: {result[2]}")
                            except Exception as e:
                                print(e)

                            try:
                                st.write(f"Followers: {result[3]}")
                            except Exception as e:
                                print(e)

                            st.divider()

                st.header('Hashtags')
                for result in results_hashtags:
                    with st.container():
                        if result :
                            try:
                                st.write(f"{result['hashtag']}")
                            except Exception as e:
                                print(e)

                            st.divider()

                st.header('Tweets')
                for result in results_tweets:
                    with st.container():
                        if result :
                            try:
                                st.write(f"{result[0]}")
                            except Exception as e:
                                print(e)

                            try:
                                st.write(f"Tweet: {result[1]}")
                            except Exception as e:
                                print(e)

                            try:
                                st.write(f"Retweets: {result[9]} \t\t  Likes: {result[10]}")
                            except Exception as e:
                                print(e)

                            st.divider()



                if not found:
                    c_data = {'Tweets': results_tweets, 'Users':results_users, 'Hashtags':results_hashtags}
                    cache[search_query] = c_data
        

    elif tab == "Trending":
        st.title("Trending")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Get top users"):
                top_users = find_top_10_users()
                st.subheader("Top Users")

                # Create a table to display the top users
                for user in top_users:
                    st.write(f"Screen Name: @{user[1]}")
                    st.write(f"Name: {user[2]}")
                    st.write(f"Description: {user[3]}")
                    st.write(f"Followers: {user[0]}")
                    st.divider()
        with col2:
            if st.button("Get Trending Hashtags"):
                top_hashtags = find_top_hashtags()
                for hashtag in top_hashtags:
                    st.write(hashtag['hashtag']['text'])

if __name__ == "__main__":
    main()
