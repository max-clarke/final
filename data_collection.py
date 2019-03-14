import pylast
import pickle
import pandas as pd
import time
import Levenshtein.StringMatcher as leven
import numpy as np

import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials

import psycopg2

# set up spotipy api
client_id='75ceaa8e4ccd4810b1995ee82aafd5e3'
client_secret='04a0d2e14c424f259132ff86275e5503'
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
sp.trace=False

# set up lastfm api
API_KEY = "e1c4eb5ed5eec78f43ff7d2c82fe033a"  
API_SECRET = "0776e51b111136a002f9f10a724460dc"

username = "jmclarke94"
password_hash = pylast.md5("Xkcd94!!")

network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET,
                                   username=username, password_hash=password_hash)

# psql setup
connection = psycopg2.connect(user="max",
                              password="password",
                              host="127.0.0.1",
                              port="5432",
                              database="final")

cursor = connection.cursor()


def users2data():
    """
    Takes list of last.fm users and retrieve top tracks for each user. Put it into sparse
    matrix (column, row, value) like dataframe.
    """
    
    with open('user_list.p', 'rb') as f:
        user_list = pickle.load(f)

    data = []
    for user in user_list:
        try:
            top_tracks = user.get_top_tracks(period='overall', limit=500)
            time.sleep(.2) # can't exceed 5 requests per second
            artist_track_names = [track.item.artist.name + ' ' + track.item.get_name() for track in top_tracks]         
            weights = [track.weight for track in top_tracks]
            username = user.name
            data.append((username, list(zip(artist_track_names, weights))))            

            # psql insertion
            q = """INSERT INTO lastfm (lastfm_user, arist_track, listen_count) VALUES (%s,%s,%s)"""
            for atn, w in zip(artist_track_names, weights):
                if len(atn) < 255:
                    record_to_insert = (username, atn, w)
                    cursor.execute(q, record_to_insert)
                    connection.commit()

                    
        except:
            print(user.name, ' failed!')
            continue


    with open('prelim_user_data.p', 'wb') as f:
        pickle.dump(data, f)
        

def expand_userlist(userlist):
    # You have to have your own unique two values for API_KEY and API_SECRET
    # Obtain yours from https://www.last.fm/api/account/create for Last.fm
    

    def user_list_descend(user_list):
        new_user_list = []

        for user in user_list:
            try:
                friends = user.get_friends()
                for friend in friends:
                    if friend not in new_user_list:
                        new_user_list.append(friend)
                        time.sleep(.2)
                        count += 1
                        if count % 50 == 0:
                            print('current length of new new list:\n', len(new_user_list))
            except:
                continue  # just skip this user

        return new_user_list

    print('exploring userlist')
    
    new_user_list = user_list_descend(user_list)
    print(f'current length is:\t {len(new_user_list)}')
    print()
    print('finished exploring userlist')

    with open('new_user_list.p', 'wb') as f:
        pickle.dump(new_user_list, f)

    print('finished saving file')


def get_features(artist_track, tolerance=10, verbose=False):
    """
    artist_track = 'artist name' + 'track name'
    
    returns: dictionary containing echonest features for that tracks
    """
    
    # make query
    results = sp.search(q=artist_track, limit=5)
    
    tracks = results['tracks']['items'] 
    
    # makes sure a match was returned:
    if tracks == []:
        print('no track found for {}'.format(artist_track))
        return 
    
    # make sure we have a convincing match
    best_distance = np.inf
    best_track = None
    for track in tracks:
        val_artist = track['artists'][0]['name']
        val_name = track['name']
        val_string = val_artist + ' ' + val_name
        val_string = val_string.lower()

        true_string = artist_track.lower()

        dist = leven.distance(true_string, val_string)
        
        
        if dist < best_distance:
            
            best_distance = dist
            best_track = track
            best_track_artist_track = val_string
            spotify_string = val_artist + ' ' + val_name
        
        
    if best_distance < tolerance:
        if verbose:
            print('===================')
            print('found match!')
            print('best distance:\t', best_distance)
            print('input:\t', artist_track)
            print('found:\t', spotify_string)
            print('====================')
            print()
        uri = best_track['uri']
        features = sp.audio_features([uri])
        return best_track_artist_track, features
        
    else:
        if verbose:
            print('+++++++++++++++++++')
            print(f'no match for {artist_track}')
            print()
            print('input:\t', artist_track)
            print('found:\t', spotify_string)
            print('+++++++++++++++++++')
        return None
    
def make_spotify_row(lastfm_artist_track):
    test_dict = get_features(lastfm_artist_track)
    if test_dict == None:
        return None
    keys = [
        'danceability',
        'energy',
        'key',
        'loudness',
        'mode',
        'speechiness',
        'acousticness',
        'instrumentalness',
        'liveness',
        'valence',
        'tempo',
        'uri',
        'analysis_url',
        'duration_ms',
        'time_signature'
    ]

    spotify_artist_track = test_dict[0]
    d = test_dict[1][0]
    try:
        features = tuple(d[key] for key in keys)
    except TypeError:
        print(f'Type Error on {lastfm_artist_track}')
        return None
        
    row = (lastfm_artist_track, spotify_artist_track) + features
    return row

def spotify_insert_row(lastfm_track, table='spotify_features'):
    q = f"""
    INSERT INTO 
        {table} (
            lastfm_artist_track,
            spotify_artist_track,
            danceability,
            energy,
            key,
            loudness,
            mode,
            speechiness,
            acousticness,
            instrumentalness,
            liveness,
            valence,
            tempo,
            uri,
            analysis_url,
            duration_ms,
            time_signature
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    ON CONFLICT
        DO NOTHING ;
    """
    row = make_spotify_row(lastfm_track)
    if row == None:
        return None
        
    cursor.execute(q, row)
    connection.commit()
        
