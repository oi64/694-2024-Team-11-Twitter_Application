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

                print(data['favorite_count'])
                if data['text'].startswith('RT'):
                    continue
                else:
                    print(data['favourites_count'])
                    # tweet["_id"] = data["id_str"]
                    # tweet["text"] = data['text']
                    # tweet["user"] = data['user']['screen_name']
                    # tweet["created_at"] = data['created_at']
                    # tweet["sentiment_score"] = sentiment_score(data['text'])
                    # tweet["user_influence"] = user_influence(data['user'])
                    # tweet["credibility_score"] = credibility_score(data['user'])
                    # tweet["engagement_rate"] = engagement_rate(data)
                    # tweet["recency_score"] = recency_score(data)
                    # tweet["media_score"] = media_score(data)
                    tweet['favourites_count'] = data['favourites_count']
                    
                collection.insert_one(tweet)
            except Exception as e:
                print(e)
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

import pymongo
import json
from tqdm import tqdm
from sentence_transformers import SentenceTransformer

def full_processing_pipeline(filename):
    # Connect to MongoDB
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client['twitter']

    # Load and insert raw data into the 'RawData' collection
    with open(filename, "r") as file:
        tweets = [json.loads(line) for line in tqdm(file) if line.strip()]
        collection = db['RawData']
        collection.insert_many(tweets)
        print(f"Inserted {len(tweets)} documents into RawData.")

    # Define the projection for transformation
    pipeline_transform = [
        {
            '$project': {
                '_id': 1, 
                'created_at': 1, 'id': 1, 'text': 1, 'source': 1, 'truncated': 1,
                'in_reply_to_status_id': 1, 'in_reply_to_user_id': 1, 'in_reply_to_screen_name': 1,
                'user_id': '$user.id', 'display_name': '$user.name', 'profile_name': '$user.screen_name',
                'user_is_protected': '$user.protected', 'user_is_verified': '$user.verified',
                'user_follower_count': '$user.followers_count', 'user_friends_count': '$user.friends_count',
                'user_listed_count': '$user.listed_count', "user_created_at": "$user.created_at",
                'geo': 1, "coordinates": 1, "place": 1, "contributors": 1, "is_quote_status": 1,
                "quote_count": 1, "reply_count": 1, "retweet_count": 1, "favorite_count": 1,
                "favorited": 1, "retweeted": 1, "possibly_sensitive": 1, "filter_level": 1, "lang": 1,
                "timestamp_ms": 1,
                'hashtags': "$entities.hashtags", 'urls': "$entities.urls", 
                "user_mentions": "$entities.user_mentions", 'symbols': "$entities.symbols"
            }
        }
    ]
    transformed_docs = list(db['RawData'].aggregate(pipeline_transform))
    db['TweetsData'].insert_many(transformed_docs)
    print(f"Transformed and inserted {len(transformed_docs)} documents into TweetsData.")

    # Aggregate and index for user ID -> Tweet._id mapping
    pipeline_user = [
        {'$group': {'_id': '$user_id', 'ids': {'$push': '$_id'}}},
        {'$project': {'user_id': '$_id', '_id': 0, 'ids': 1}}
    ]
    user_docs = list(db['TweetsData'].aggregate(pipeline_user))
    db['Userid-Tweets._id'].insert_many(user_docs)
    db['Userid-Tweets._id'].create_index([('user_id', pymongo.ASCENDING)])
    print(f"Indexed {len(user_docs)} user documents in Userid-Tweets._id.")

    # Aggregate and index for hashtags -> Tweet._id mapping
    pipeline_hashtag = [
        {'$unwind': '$hashtags'},
        {'$group': {'_id': '$hashtags', 'ids': {'$push': '$_id'}}},
        {'$project': {'hashtag': '$_id', '_id': 0, 'ids': 1}}
    ]
    hashtag_docs = list(db['TweetsData'].aggregate(pipeline_hashtag))
    db['Hashtags-Tweets._id'].insert_many(hashtag_docs)
    db['Hashtags-Tweets._id'].create_index([('hashtag', pymongo.ASCENDING)])
    print(f"Indexed {len(hashtag_docs)} hashtag documents in Hashtags-Tweets._id.")

    # Close the MongoDB connection
    return None


def main():
    client, db, collection = connect_to_mongodb(database_name, collection_name)
    # if collection.count_documents({}) == 0:
    if True:
        insert_tweets_from_file(collection)
    # if db['RawData'].count_documents({}) == 0:
    #     full_processing_pipeline(filename)
    # if True:#client is not None and db is not None and collection is not None:
    #         print(f'Database: {db}\nCollection: {collection}')
    #         if True: #not any('text_embeddings' in doc for doc in collection.find()):
    #             add_tweet_embeddings_to_documents(collection)
    #             cluster_tweets_and_save_to_collections(collection, db)
    #             calculate_and_save_cluster_centroids(db)
    #         else:
    #             print("Embeddings already exist in some documents. Skipping the functions.")
    #
    #         # Print cluster centroids
    #         print_cluster_centroids(db['tweet_cluster_centroids'])
    #         # Print collection names
    #         print_collection_names(db)
    #
    #         # Close the MongoDB connection
    #         client.close()
    # else:
    #     print("Connection to MongoDB failed.")


if __name__ == "__main__":  
    main()
    # insert_tweets_from_file()

