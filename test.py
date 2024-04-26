
from MongoDBConnector import connect_to_mongodb, database_name, collection_name, filename
import json
from sklearn.metrics.pairwise import euclidean_distances
from sentence_transformers import SentenceTransformer

client, db, collection = connect_to_mongodb(database_name, collection_name)

def delete_all_collections():
    
    if db is not None:
        # List all collections
        collections = db.list_collection_names()
        print(f"Found collections: {collections}")
        
        # Delete each collection
        for collection in collections:
            db.drop_collection(collection)
            print(f"Deleted collection: {collection}")
        
        print("All collections have been deleted.")
    else:
        print("Failed to access the database.")

    if client is not None:
        client.close()

def print_collection_names(db):
    print(db.list_collection_names())

print_collection_names(db)

##
delete_all_collections()


# from sklearn.cluster import KMeans
# import numpy as np
#
# # Example data
# X = np.random.rand(100, 5)
# kmeans = KMeans(n_clusters=5)
# kmeans.fit(X)

