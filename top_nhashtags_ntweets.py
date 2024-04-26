from pymongo import MongoClient
import pymongo
from pymongo.server_api import ServerApi

def getTopNTweetsOnce():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client['twitter']
    source_collection = db['TweetsData2.0']
    target_collection = db['TopNTweets']
    """
    Top 10 Tweets sorted on tweet score.
    tweet_score = like + 2*reply_count + 3*retweet_count
    """
    source_tweets_data = source_collection.find({
        "in_reply_to_status_id": None,
    })
    source_tweets_data = list(source_tweets_data)
    for i in source_tweets_data:
        i['tweet_score'] = 3*int(i['quote_count']) + 2*int(i['reply_count']) + 4*(i['retweet_count'])+ i['favorite_count']
    topntweets = sorted(list(source_tweets_data), key=lambda d: d['tweet_score'],reverse=True)[:10]
    target_collection.drop()
    target_collection.insert_many(topntweets)
    return


def getTopNHashtagsOnce():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client['twitter']
    source_collection = db['Hashtags-Tweets._id']
    target_collection = db['TopNHashtags']
    pipeline = [
        {'$unwind': "$hashtag"},
        {'$group': {
            '_id': "$hashtag.text",
            'count': {'$sum': 1},
            'ids': {'$push': "$_id"}
        }},
        {'$sort': {'count': -1}},
        {'$limit': 10}
    ]
    source_hashtags_data = source_collection.aggregate(pipeline)

    source_hashtags_data = list(source_hashtags_data)
    topnhashtags = sorted(list(source_hashtags_data), key=lambda d: d['count'], reverse=True)[:10]
    target_collection.drop()
    target_collection.insert_many(topnhashtags)
    return

def getTopNTweets(collection_name):
    collection_name.collection_name.find({})
    return list(collection_name)

def getTopNHashtags(collection_name):
    collection_name.collection_name.find({})
    return list(collection_name)