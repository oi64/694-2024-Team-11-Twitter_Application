##
import pymongo
import popularity
# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")

# Create a new database
db = client["twitter"]

# Create a new collection
collection = db["tweet_cluster_centroids"]


print(popularity.return_top_5("election",collection))