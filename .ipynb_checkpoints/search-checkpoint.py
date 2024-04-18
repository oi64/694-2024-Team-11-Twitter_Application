import toml
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import euclidean_distances
import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017/")

# Create a new database
db = client["twitter"]

# Create a new collection
collection = db["tweet_cluster_centroids"]

is_empty = collection.count_documents({}) == 0

if is_empty:
    print("Collection is empty")
else:
    print("Collection is not empty")

def search(input_keyword, db = db, collection = collection):
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
