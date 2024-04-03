##
import json
import User
from MySQLConnector import MySQLConnector
import Constants

##
lines = 0
num_tweets = 0
num_retweets = 0
tweets = {}
error_count = 0
users = {}

# insert path and replace name of the file below as needed
filename = "data/corona-out-2"
with open(filename, "r") as f1:
    for line in f1:
        try:
            data = json.loads(line)
            lines = lines + 1
            user = data['user']
            if (data['text'].startswith('RT')):
                num_retweets += 1
            else:
                num_tweets += 1
            if (data['id_str'] not in tweets):
                tweets[data['id_str']] = data
            if user['id_str'] not in users:
                users[user['id_str']] = user
        except:
            # if there is an error loading the json of the tweet, skip
            error_count += 1
            continue

print('num of lines=', lines, 'num of tweets=', num_tweets, 'num of retweets=', num_retweets)
print('num of unique tweets/retweets=', len(tweets.keys()))
print('num of unique users=', len(users.keys()))
print("error count: ", error_count)

##
connector = MySQLConnector()
connector.get_server_connection()

##
for ID, user_itr in users.items():
    user_instance = User.User(user_itr)
    query = Constants.INSERT_USER_QUERY
    connector.execute_query(query, User.get_user_tuple(user_instance))

connector.close_server_connection()
