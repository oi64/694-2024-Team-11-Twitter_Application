from popular_users import find_top_10_users, find_top_hashtags
import threading
import time
import json
from collections import OrderedDict

cache = {'Static':{
    'Users': find_top_10_users(),
    'Hashtags': find_top_hashtags()
},
}



def save_cache_state():
    """Saves the current state of the cache to a JSON file."""
    try:
        # Define the filename where the cache will be saved
        filename = 'cache_state.json'
        
        # Open the file in write mode and dump the cache as JSON
        with open(filename, 'w') as f:
            json.dump(str(cache), f, indent=4)  # Use `indent` for pretty-printing
        
        print("Cache state saved successfully.")
    except Exception as e:
        print(f"An error occurred while saving the cache: {e}")



def cache_saving_task():
    while True:
        save_cache_state()  # Call the function to save cache state
        time.sleep(60)  # Wait for 300 seconds (5 minutes)



def start_background_task():
    thread = threading.Thread(target=cache_saving_task)
    thread.daemon = True  # Set as a daemon so it will be killed once the main thread is dead.
    thread.start()


def update_cache(key, data, max_cache_size=3):
    # Operate only on the 'Dynamic' part of the cache
    dynamic_cache = cache['Dynamic']

    # Remove the least recently accessed item if necessary
    
    if dynamic_cache and key not in dynamic_cache and len(dynamic_cache) >= max_cache_size:
        oldest_key, oldest_value = dynamic_cache.popitem(last=False)
        print(f"Removed least recently accessed item: {oldest_key}")

    # Update or add new data and mark as recently used
    dynamic_cache[key] = data
    dynamic_cache.move_to_end(key)
    # print(dynamic_cache)