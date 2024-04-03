from datetime import datetime


def get_user_tuple(user_instance):
    values = (
        user_instance.id, user_instance.id_str, user_instance.name, user_instance.screen_name,
        user_instance.location,
        user_instance.url, user_instance.description, user_instance.protected, user_instance.verified,
        user_instance.followers_count, user_instance.friends_count, user_instance.listed_count,
        user_instance.favourites_count, user_instance.statuses_count, user_instance.created_at,
        user_instance.geo_enabled,
        user_instance.lang, user_instance.contributors_enabled
    )
    return values


class User:
    def __init__(self, user_data):
        self.id = user_data.get('id')
        self.id_str = user_data.get('id_str')
        self.name = user_data.get('name')
        self.screen_name = user_data.get('screen_name')
        self.location = user_data.get('location')
        self.url = user_data.get('url')
        self.description = user_data.get('description')
        self.protected = user_data.get('protected')
        self.verified = user_data.get('verified')
        self.followers_count = user_data.get('followers_count')
        self.friends_count = user_data.get('friends_count')
        self.listed_count = user_data.get('listed_count')
        self.favourites_count = user_data.get('favourites_count')
        self.statuses_count = user_data.get('statuses_count')
        self.created_at = int(
            datetime.strptime(user_data.get('created_at'), "%a %b %d %H:%M:%S %z %Y").timestamp()) if user_data.get(
            'created_at') else None
        self.geo_enabled = user_data.get('geo_enabled')
        self.lang = user_data.get('lang')
        self.contributors_enabled = user_data.get('contributors_enabled')
