# from MongoDBConnector import connect_to_mongodb, database_name, collection_name, filename
# import json
# from sklearn.metrics.pairwise import euclidean_distances
# from sentence_transformers import SentenceTransformer

# client, db, collection = connect_to_mongodb(database_name, collection_name)

# def delete_all_collections():
    
#     if db is not None:
#         # List all collections
#         collections = db.list_collection_names()
#         print(f"Found collections: {collections}")
        
#         # Delete each collection
#         for collection in collections:
#             db.drop_collection(collection)
#             print(f"Deleted collection: {collection}")
        
#         print("All collections have been deleted.")
#     else:
#         print("Failed to access the database.")

#     if client is not None:
#         client.close()

# def print_collection_names(db):
#     print(db.list_collection_names())

# print_collection_names(db)
# delete_all_collections()

# # collection.find_one({"_id": f"cluster_{1}"})
# # def search(input_keyword):
# #     model = SentenceTransformer('all-mpnet-base-v2')
# #     vector_of_input_keyword = model.encode(input_keyword)

# #     # Find the closest cluster to the input vector
# #     closest_cluster = None
# #     min_distance = float('inf')
# #     print(collection.find_one({}))
# #     for i in range(7):  # Assuming 7 clusters tweet_cluster_0 to tweet_cluster_6
# #         centroid_doc = collection.find_one({"_id": f"cluster_{i}"})
# #         centroid = centroid_doc["centroid"]
# #         distance = euclidean_distances([vector_of_input_keyword], [centroid])[0][0]
# #         if distance < min_distance:
# #             min_distance = distance
# #             closest_cluster = i

# #     closest_cluster_collection = db[f"tweet_cluster_{closest_cluster}"]
# #     tweets_in_cluster = closest_cluster_collection.find()
# #     tweet_vectors = [tweet["text_embeddings"] for tweet in tweets_in_cluster]

# #     # Calculate L2 norm distances
# #     distances = euclidean_distances([vector_of_input_keyword], tweet_vectors)[0]

# #     # Get indices of top 5 tweets
# #     top_5_indices = distances.argsort()[:5]

# #     # Retrieve top 5 tweets
# #     tweets_in_cluster = closest_cluster_collection.find()
# #     all_tweets = [[_tweet["user"],_tweet["text"]] for _tweet in tweets_in_cluster]
# #     top_5_tweets = [all_tweets[i] for i in top_5_indices]

# #     return top_5_tweets

# # print(search('trump'))
from sklearn.cluster import KMeans
import numpy as np

# Example data
X = np.random.rand(100, 5)
kmeans = KMeans(n_clusters=5)
kmeans.fit(X)