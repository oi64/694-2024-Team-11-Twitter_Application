INSERT_USER_QUERY = """
    INSERT INTO twitter_users (id, id_str, name, screen_name, location, url, description, protected, verified,
    followers_count, friends_count, listed_count, favourites_count, statuses_count, created_at, geo_enabled, lang,
    contributors_enabled) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""
