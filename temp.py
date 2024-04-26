##

from popular_users import find_top_10_users, find_top_hashtags


##
users = find_top_10_users()
user_data = [[user[1], user[2], user[3], user[4]] for user in users]
hashtags = find_top_hashtags()
print(hashtags)