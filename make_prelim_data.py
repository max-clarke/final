import pylast
import pickle
import pandas as pd
import time

with open('user_list.p', 'rb') as f:
    user_list = pickle.load(f)
    
data = []
for user in user_list:
    try:
        top_artists = user.get_top_artists()
        time.sleep(.05)
        artist_names = [artist.item.name for artist in top_artists]
        weights = [artist.weight for artist in top_artists]
        username = user.name
        data.append((username, list(zip(artist_names, weights))))
    except:
        print(user.name, ' failed!')
        continue
        
with open('prelim_user_data.p', 'wb') as f:
    pickle.dump(data, f)