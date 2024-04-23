##
import pymongo
import json
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from collections import Counter
from tqdm import tqdm
import numpy as np
from popularity import sentiment_score, user_influence, credibility_score, engagement_rate,recency_score, media_score
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
        print('database connected')
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
        for line in tqdm(f1):
            tweet = {}
            try:
                data = json.loads(line)

                if data['text'].startswith('RT'):
                    continue
                else:
                    tweet["_id"] = data["id_str"]
                    tweet["text"] = data['text']
                    tweet["user"] = data['user']['screen_name']
                    tweet["created_at"] = data['created_at']
                    tweet["sentiment_score"] = sentiment_score(data['text'])  
                    tweet["user_influence"] = user_influence(data['user']) 
                    tweet["credibility_score"] = credibility_score(data['user'])
                    tweet["engagement_rate"] = engagement_rate(data)  
                    tweet["recency_score"] = recency_score(data)  
                    tweet["media_score"] = media_score(data) 
                    
                collection.insert_one(tweet)
            except Exception as e:
                # if there is an error loading the json of the tweet, skip
                error_count += 1
                # print(f"Error inserting tweet: {e}")
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

    print('Added tweet embeddings')

def cluster_tweets_and_save_to_collections(collection, db, n_clusters = 15):
    documents = list(collection.find({}))
    X = np.array([doc['text_embeddings'] for doc in documents])
    print(X.shape)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    kmeans = KMeans(n_clusters, random_state=0)
    print(X_scaled)
    kmeans.fit(X_scaled)
    labels = kmeans.labels_

    for i, label in enumerate(labels):
        cluster_collection = db[f'tweet_cluster_{label}']
        cluster_collection.insert_one(documents[i])


    print(f'Clustered and added tweets, num clusters = {n_clusters}')

def calculate_and_save_cluster_centroids(db, num_centroids = 15):
    centroids = []

    for i in range(num_centroids):
        cluster_collection = db[f'tweet_cluster_{i}']
        documents = list(cluster_collection.find())
        embeddings = np.array([doc['text_embeddings'] for doc in documents])
        centroid = np.mean(embeddings, axis=0)
        centroids.append(centroid.tolist())

        centroids_collection = db['tweet_cluster_centroids']
        centroids_collection.insert_one({'_id': f'cluster_{i}', 'centroid': centroid.tolist()})

    print('saved cluster centroids')

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
    if True:#client is not None and db is not None and collection is not None:
            print(f'Database: {db}\nCollection: {collection}')
            if True: #not any('text_embeddings' in doc for doc in collection.find()):
                add_tweet_embeddings_to_documents(collection)
                cluster_tweets_and_save_to_collections(collection, db)
                calculate_and_save_cluster_centroids(db)
            else:
                print("Embeddings already exist in some documents. Skipping the functions.")

            # Print cluster centroids
            print_cluster_centroids(db['tweet_cluster_centroids'])
            # Print collection names
            print_collection_names(db)

            # Close the MongoDB connection
            client.close()
    else:
        print("Connection to MongoDB failed.")


if __name__ == "__main__":  
    main()


