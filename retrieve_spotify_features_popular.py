# goal: implement levenshtein distance to validate correct result
# go from lastfm tracks to spotify features for that track
import data_collection
import time
import psycopg2
import numpy as np
from random import shuffle

print('connecting to postgres...')
connection = psycopg2.connect(user="max",
                              password="password",
                              host="127.0.0.1",
                              port="5432",
                              database="final")
print()
print(connection)
cursor = connection.cursor()

# # create a new postgres table for our popular tracks
# q = """
# CREATE TABLE popular_spotify_features (
#     lastfm_artist_track VARCHAR (255) NOT NULL,
#     spotify_artist_track VARCHAR (255) NOT NULL,
#     danceability NUMERIC NOT NULL,
#     energy NUMERIC NOT NULL,
#     key NUMERIC NOT NULL,
#     loudness NUMERIC NOT NULL,
#     mode NUMERIC NOT NULL,
#     speechiness NUMERIC NOT NULL,
#     acousticness NUMERIC NOT NULL,
#     instrumentalness NUMERIC NOT NULL,
#     liveness NUMERIC NOT NULL,
#     valence NUMERIC NOT NULL,
#     tempo NUMERIC NOT NULL,
#     uri VARCHAR (255) NOT NULL,
#     analysis_url VARCHAR (255) NOT NULL,
#     duration_ms NUMERIC NOT NULL,
#     time_signature SMALLINT NOT NULL
# );
# """

# cursor.execute(q)
# connection.commit()

# let's only get top tracks
q = """
SELECT arist_track FROM lastfm
    GROUP BY arist_track
    HAVING COUNT(lastfm_user) > 8 
;
"""

cursor.execute(q)
lastfm_tracks = cursor.fetchall()

print('beggining psql insertion...')
print()

# Get spotify features and insert into psql table
for track in lastfm_tracks:
    data_collection.spotify_insert_row(track[0], table='popular_spotify_features')
    time.sleep(.08)

