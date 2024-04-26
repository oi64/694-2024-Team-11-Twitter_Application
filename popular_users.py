from MySQLConnector import MySQLConnector
import pymongo


def search_users_by_keyword(keyword):
    connector = MySQLConnector()
    connector.get_server_connection()
    
    query = """
        SELECT id, name, description, followers_count
        FROM twitter_users
        WHERE description LIKE %s OR name LIKE %s
        ORDER BY followers_count DESC
        LIMIT 10;
    """
    # Use % to denote wildcard matches before and after the keyword
    values = (f"%{keyword}%", f"%{keyword}%")
    
    results = connector.execute_query(query, values)
    
    # for user in results:
    #     print(user)  # Print each user found by the query

    return results
    
def find_top_10_users():
    connector = MySQLConnector()
    connector.get_server_connection()
    
    query = """
        SELECT id, name, description, followers_count
        FROM twitter_users
        ORDER BY followers_count DESC
        LIMIT 10;
    """

    # values = (f"%{keyword}%", f"%{keyword}%")
    
    results = connector.execute_query(query)
    return results

def find_top_hashtags(db_name='twitter', collection_name='Hashtags-Tweets._id'):
    # Connect to MongoDB
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client[db_name]
    collection = db[collection_name]

    # Aggregation pipeline to find top 10 hashtags with the most tweet IDs
    pipeline = [
        {'$project': {
            'hashtag': '$hashtag',  # Project the hashtag field
            'num_ids': {'$size': '$ids'}  # Calculate the size of the ids array
        }},
        {'$sort': {'num_ids': -1}},  # Sort documents by num_ids in descending order
        {'$limit': 20}  # Limit the result to the top 10
    ]

    # Execute the aggregation pipeline
    result = list(collection.aggregate(pipeline))

    # Close the MongoDB connection
    client.close()
    seen = []
    i = 0
    # Print the results
    for doc in result:
        if doc['hashtag']['text'].lower() not in seen:
            #print(f"Hashtag: {doc['hashtag']['text']}, Count of Tweets: {doc['num_ids']}")
            seen.append(doc['hashtag']['text'].lower())
            i+=1
            if i == 10:
                break
        else:
            continue

    return result



# Example usage
if __name__ == "__main__":
    keyword = input("Enter a keyword to search in users: ")
    results = search_users_by_keyword(keyword)

    print(find_top_hashtags())
    print(results)
