##
import pymongo
import json
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from collections import Counter
import numpy as np
##
# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")

# Create a new database
db = client["twitter"]

# Create a new collection
collection = db["tweet_embeddings"]

##
filename = "data/corona-out-2"
error_count = 0


with open(filename, "r") as f1:
    for line in f1:
        tweet = {}
        try:
            data = json.loads(line)

            if (data['text'].startswith('RT')):
                continue
            else:
                tweet["_id"] = data["id_str"]
                tweet["text"] = data['text']
                tweet["user"] = data['user']['screen_name']
                # tweet_encoding = get_tweet_encodings(data['text'])
                # tweet["text_embeddings"] = tweet_encoding.tolist()
            collection.insert_one(tweet)
        except:
            # if there is an error loading the json of the tweet, skip
            error_count += 1
            continue


##
# Function to get tweet encodings in batches
def get_tweet_encodings_in_batches(bulk_documents):
    model = SentenceTransformer('all-mpnet-base-v2')
    tweet_texts = [tweet['text'] for tweet in bulk_documents]
    tweet_encodings = model.encode(tweet_texts)
    return tweet_encodings


# Initialize an empty list to store the bulk operations
bulk_operations = []
bulk_documents = []
batch_size = 1000

# Iterate over the documents in the collection and add the "text_embeddings" field
for document in collection.find():
    bulk_documents.append(document)
    # Execute bulk update every batch_size documents
    if len(bulk_documents) == batch_size:
        tweet_encodings = get_tweet_encodings_in_batches(bulk_documents)
        for document, tweet_encoding in zip(bulk_documents, tweet_encodings):
            collection.update_one(
                {"_id": document["_id"]},
                {"$set": {"text_embeddings": tweet_encoding.tolist()}}
            )
        bulk_operations = []
        bulk_documents = []

tweet_encodings = get_tweet_encodings_in_batches(bulk_documents)
for document, tweet_encoding in zip(bulk_documents, tweet_encodings):
    collection.update_one(
        {"_id": document["_id"]},
        {"$set": {"text_embeddings": tweet_encoding.tolist()}}
    )


##
# Get the size of the collection
# Get the stats for the collection
collection_stats = db.command("collstats", "tweet_embeddings")
print(collection_stats)

##


# Fetch documents from MongoDB
documents = list(collection.find())

# Extract text embeddings from documents
X = np.array([doc['text_embeddings'] for doc in documents])

# Normalize the data
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Fit KMeans clustering
kmeans = KMeans(n_clusters=7, random_state=0)
kmeans.fit(X_scaled)

# Get cluster labels
labels = kmeans.labels_

##
# Count the frequency of each element
frequency = Counter(labels)

# Print the frequency of each element
for element, count in frequency.items():
    print(f"Element {element} appears {count} times")
##
# Save the clusters into different collections
for i, label in enumerate(labels):
    cluster_collection = db[f'tweet_cluster_{label}']
    cluster_collection.insert_one(documents[i])

##
# Define the range of cluster collections
cluster_range = range(7)

# Initialize an empty list to store centroids
centroids = []

# Iterate over each cluster collection
for i in cluster_range:
    # Get the current cluster collection
    cluster_collection = db[f'tweet_cluster_{i}']

    # Get all documents from the current cluster collection
    documents = list(cluster_collection.find())

    # Extract text embeddings from documents
    embeddings = np.array([doc['text_embeddings'] for doc in documents])

    # Calculate the centroid
    centroid = np.mean(embeddings, axis=0)

    # Append the centroid to the list of centroids
    centroids.append(centroid.tolist())

    centroids_collection = db['tweet_cluster_centroids']

    centroids_collection.insert_one({'_id':'cluster_' + str(i),'centroid': centroid.tolist()})

##
collection = db['tweet_cluster_centroids']

# Print all documents in the collection
for document in collection.find():
    print(document)

##
print(client.list_database_names())

##
print(db.list_collection_names())

##
centroids_collection = db['tweet_cluster_centroids']
centroids_collection.delete_many({})

# ##
# # Get the list of collection names in the database
# collection_names = db.list_collection_names()
#
# # Drop each collection in the database
# for collection_name in collection_names:
#     db.drop_collection(collection_name)


