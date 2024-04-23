
from search import search_cache
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import euclidean_distances
from sentence_transformers import SentenceTransformer
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
# nltk.download('vader_lexicon')
from datetime import datetime
import pymongo
import heapq
import numpy as np

database_name = 'twitter'
collection_name = 'tweet_embeddings'
filename = "data/corona-out-2"

def download_vader_if_not_exist():
    try:
        nltk.data.find('sentiment/vader_lexicon.zip')
    except LookupError:
        # If not found, download it
        print("vader_lexicon not found, downloading...")
        nltk.download('vader_lexicon')
        print("Download complete.")
    else:
        print("vader_lexicon is already downloaded.")


def connect_to_mongodb(database_name, collection_name):
    try:
        client = pymongo.MongoClient("mongodb://localhost:27017/")

        if database_name not in client.list_database_names():
            db = client[database_name]
            # print(f"Database '{database_name}' created.")
        else:
            db = client[database_name]
        # print('database connected')
        if collection_name not in db.list_collection_names():
            collection = db[collection_name]
            # print(f"Collection '{collection_name}' created in database '{database_name}'.")
        else:
            collection = db[collection_name]

        return client, db, collection

    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None, None, None

client, db, collection = connect_to_mongodb(database_name, collection_name)


def topic_relevance(text, topic_keywords):
    words = set(text.lower().split())
    relevant_words = words.intersection(set(topic_keywords))
    return len(relevant_words) / len(topic_keywords) if topic_keywords else 0


def rankTweets(vector_of_input_keyword, closest_cluster):
    closest_cluster_collection = db[f"tweet_cluster_{closest_cluster}"]
    tweets_in_cluster = closest_cluster_collection.find()
    tweet_vectors = [tweet["text_embeddings"] for tweet in tweets_in_cluster]

    # Calculate L2 norm distances
    distances = euclidean_distances([vector_of_input_keyword], tweet_vectors)[0]

    # Get indices of top 5 tweets
    top_5_indices = distances.argsort()[:50]

    # Retrieve top 5 tweets
    tweets_in_cluster = closest_cluster_collection.find()
    all_tweets = [[_tweet["user"],_tweet["text"], _tweet["created_at"],
                   _tweet["sentiment_score"], _tweet['user_influence'],
                   _tweet['credibility_score'], _tweet['engagement_rate'],
                   _tweet['recency_score'], _tweet['media_score']] for _tweet in tweets_in_cluster]
    top_50_tweets = [all_tweets[i] for i in top_5_indices]
    return top_50_tweets


def credibility_score(user_data):
    return 1.0 if user_data['verified'] else 0.5

def engagement_rate(tweet):
    time_since_post = (datetime.now() - datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')).total_seconds() / 3600
    engagement = (tweet['retweet_count'] + tweet['favorite_count']) / max(time_since_post, 1)  # Normalize over hours since post
    return engagement



def sentiment_score(text):
    download_vader_if_not_exist()
    sia = SentimentIntensityAnalyzer()
    score = sia.polarity_scores(text)
    return score['compound']  # Return the compound score which represents an aggregate of all sentiment scores

def recency_score(tweet):
    tweet_date = datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
    age_hours = (datetime.now() - tweet_date).total_seconds() / 3600
    return max(0, 1 - (age_hours / 24))  # Decay score over 24 hours


def media_score(tweet):
    if 'extended_entities' in tweet and 'media' in tweet['extended_entities']:
        return 1
    return 0



def user_influence(user_data):

    scaler = MinMaxScaler()

    followers_count = user_data['followers_count']
    friends_count = max(user_data['friends_count'], 1)  # avoid division by zero
    influence = followers_count / friends_count
    # Scale based on some expected range of influence values
    return scaler.fit_transform([[influence]])[0][0]

def compute_score(tweet):
    weights = {
        'sentiment': 0.2,
        'influence': 0.5,
        'credibility': 0.2,
        'engagement': 0.5,
        'recency': 0.1,
        'media': 0.1
    }

    features = {
        'sentiment': tweet[3],
        'influence': tweet[4],
        'credibility': tweet[5],
        'engagement': tweet[6],
        'recency': tweet[7],
        'media': tweet[8]
    }

    # Normalize features to a common scale if necessary
    scaler = MinMaxScaler()
    scaled_features = scaler.fit_transform(np.array(list(features.values())).reshape(-1, 1)).flatten()

    # Calculate weighted score
    score = sum(weight * feature for weight, feature in zip(weights.values(), scaled_features))

    return score


def return_top_5(input_keyword, collection, n_clusters = 15):
    # Retrieve the top 50 tweets from a function that ranks them

    model = SentenceTransformer('all-mpnet-base-v2')
    vector_of_input_keyword = model.encode(input_keyword)

    closest_cluster = None
    min_distance = float('inf')
    for i in range(n_clusters):  
        centroid_doc = collection.find_one({"_id": f"cluster_{i}"})
        centroid = centroid_doc["centroid"]
        distance = euclidean_distances([vector_of_input_keyword], [centroid])[0][0]
        if distance < min_distance:
            min_distance = distance
            closest_cluster = i
    top_50_tweets = rankTweets(vector_of_input_keyword, closest_cluster)

    min_heap = []

    for tweet in top_50_tweets:
        score = compute_score(tweet)
        
        heapq.heappush(min_heap, (-score, tweet))
        
        if len(min_heap) > 5:
            heapq.heappop(min_heap)
    top_5_tweets = []
    while min_heap:
        top_5_tweets.append(heapq.heappop(min_heap)[1])

    return top_5_tweets[::-1]


