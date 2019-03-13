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

# # Create new table from scratch
# q = "DROP TABLE spotify_features"

# cursor.execute(q)

# q = """
# CREATE TABLE spotify_features (
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

# Retrieve all distince lastfm artist_tracks

q = """
SELECT DISTINCT arist_track FROM lastfm;
"""
cursor.execute(q)
lastfm_artist_tracks = cursor.fetchall()
shuffle(lastfm_artist_tracks)

print('beggining psql insertion...')
print()
print(lastfm_artist_tracks[:5])

# Get spotify features and insert into psql table
for artist_track in lastfm_artist_tracks:
    data_collection.spotify_insert_row(artist_track[0])
    time.sleep(.08)

