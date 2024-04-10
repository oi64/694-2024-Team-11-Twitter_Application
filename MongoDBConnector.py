##
import pymongo
import json
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from collections import Counter
import numpy as np
##

database_name = 'twitter'
collection_name = 'tweet_embeddings'
filename = "data/corona-out-2"


def connect_to_mongodb(database_name, collection_name):
    try:
        client = pymongo.MongoClient("mongodb://localhost:27017/")

        if database_name not in client.list_database_names():
            db = client[database_name]
            print(f"Database '{database_name}' created.")
        else:
            db = client[database_name]

        if collection_name not in db.list_collection_names():
            collection = db[collection_name]
            print(f"Collection '{collection_name}' created in database '{database_name}'.")
        else:
            collection = db[collection_name]

        return client, db, collection

    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None, None, None


def insert_tweets_from_file(collection, filename = filename):
    error_count = 0

    with open(filename, "r") as f1:
        for line in f1:
            tweet = {}
            try:
                data = json.loads(line)

                if data['text'].startswith('RT'):
                    continue
                else:
                    tweet["_id"] = data["id_str"]
                    tweet["text"] = data['text']
                    tweet["user"] = data['user']['screen_name']
                    # tweet_encoding = get_tweet_encodings(data['text'])
                    # tweet["text_embeddings"] = tweet_encoding.tolist()
                collection.insert_one(tweet)
            except Exception as e:
                # if there is an error loading the json of the tweet, skip
                error_count += 1
                print(f"Error inserting tweet: {e}")
                continue
    print(f'The number of errors is {error_count}')

    return None


def get_tweet_encodings_in_batches(bulk_documents):
    model = SentenceTransformer('all-mpnet-base-v2')
    tweet_texts = [tweet['text'] for tweet in bulk_documents]
    tweet_encodings = model.encode(tweet_texts)
    return tweet_encodings

def add_tweet_embeddings_to_documents(collection, batch_size=1000):
    bulk_documents = []

    for document in collection.find():
        bulk_documents.append(document)
        if len(bulk_documents) == batch_size:
            tweet_encodings = get_tweet_encodings_in_batches(bulk_documents)
            for document, tweet_encoding in zip(bulk_documents, tweet_encodings):
                collection.update_one(
                    {"_id": document["_id"]},
                    {"$set": {"text_embeddings": tweet_encoding.tolist()}}
                )
            bulk_documents = []

    if bulk_documents:
        tweet_encodings = get_tweet_encodings_in_batches(bulk_documents)
        for document, tweet_encoding in zip(bulk_documents, tweet_encodings):
            collection.update_one(
                {"_id": document["_id"]},
                {"$set": {"text_embeddings": tweet_encoding.tolist()}}
            )

def cluster_tweets_and_save_to_collections(collection, db):
    documents = list(collection.find())
    X = np.array([doc['text_embeddings'] for doc in documents])
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    kmeans = KMeans(n_clusters=7, random_state=0)
    kmeans.fit(X_scaled)
    labels = kmeans.labels_

    for i, label in enumerate(labels):
        cluster_collection = db[f'tweet_cluster_{label}']
        cluster_collection.insert_one(documents[i])

def calculate_and_save_cluster_centroids(db, num_centroids = 7):
    centroids = []

    for i in range(num_centroids):
        cluster_collection = db[f'tweet_cluster_{i}']
        documents = list(cluster_collection.find())
        embeddings = np.array([doc['text_embeddings'] for doc in documents])
        centroid = np.mean(embeddings, axis=0)
        centroids.append(centroid.tolist())

        centroids_collection = db['tweet_cluster_centroids']
        centroids_collection.insert_one({'_id': f'cluster_{i}', 'centroid': centroid.tolist()})

def print_cluster_centroids(collection):
    for document in collection.find():
        print(document)

def print_collection_names(db):
    print(db.list_collection_names())

def delete_cluster_centroids_collection(db):
    centroids_collection = db['tweet_cluster_centroids']
    centroids_collection.delete_many({})

def main():
    client, db, collection = connect_to_mongodb(database_name, collection_name)
    if collection.count_documents({}) == 0:
        insert_tweets_from_file(collection)
    if client is not None and db is not None and collection is not None:
            # Check if embeddings already exist in any document
            if not any('text_embeddings' in doc for doc in collection.find()):
                # If embeddings do not exist, run the functions to add embeddings and cluster tweets
                add_tweet_embeddings_to_documents(collection)
                cluster_tweets_and_save_to_collections(collection, db)
                calculate_and_save_cluster_centroids(db)
            else:
                print("Embeddings already exist in some documents. Skipping the functions.")

            # Print cluster centroids
            print_cluster_centroids(db['tweet_cluster_centroids'])
            # Print collection names
            print_collection_names(db)

            # Delete cluster centroids collection
            delete_cluster_centroids_collection(db)

            # Close the MongoDB connection
            client.close()
    else:
        print("Connection to MongoDB failed.")

main()


