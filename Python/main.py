import csv
from random import seed
from random import choice

import traceback

import json

import pymongo

from pprint import pprint

from flask import Flask, request
from flask_cors import CORS

from surpriselib import gen_rec

# Flask
app = Flask(__name__)
CORS(app)

# Connect to db
client = pymongo.MongoClient(
    "mongodb+srv://dan:ontNxIMT881Cxpkg@cluster0.ufxge.mongodb.net/FYP?retryWrites=true&w=majority")
admin = client.admin
db = client["FYP"]
col = db["Users"]

try:
    serverStatusResult = admin.command("serverStatus")
    pprint(serverStatusResult)
except:
    traceback.print_exc()


@app.route("/check_rec", methods=['GET', 'POST'])
def check_rec():
    if request.method == 'POST':
        id = str(request.form.getlist('id'))[2:-2]
        cursor = list(col.find({"user": id}))
        if len(cursor) == 0:  # check for previous recommendations
            return "False"
        else:
            return "True"


@app.route("/get_prev_rec", methods=['GET', 'POST'])
def get_prev_rec():
    if request.method == 'POST':
        id = str(request.form.getlist('id'))[2:-2]
        cursor = list(col.find({"user": id}))
        return str(cursor)


@app.route("/check_dupes", methods=['GET', 'POST'])
def check_dupes():
    if request.method == 'POST':
        id = str(request.form.getlist('id'))[2:-2]
        track = str(request.form.getlist('track'))[2:-2]
        cursor = list(col.find({"user": id}))

        for saved_song in cursor:
            if str(saved_song['song']) == str(track):
                return ""

        return track


@app.route("/get_rec", methods=['GET', 'POST'])
def get_rec():
    if request.method == 'POST':
        id = str(request.form.getlist('id'))[2:-2]
        # pull all ratings > 5
        songlist = []
        genre = str(request.form.getlist('values[0][gen_val]'))[2:-2]
        cursor = list(col.find({"user": id, "genre": genre}))
        for song in cursor:
            if int(song['rating']) > 5:
                songlist.append(song)

        # take 5 of the songs > 5
        random_songs = []
        seed(1)
        range_num = 0
        if len(songlist) < 5:
            range_num = len(songlist)  # in case the user has < 5 songs rated above 5
        else:
            range_num = 5

        first = True
        duplicate = False

        for _ in range(range_num):
            appended = False

            if first == True:  # if first in list, append the song
                selection = choice(songlist)
                random_songs.append(selection)
                # print("First song: Selection" + str(selection))
                appended = True
                first = False

            while appended == False:
                selection = choice(songlist)  # choose a random song...
                # print("Ready to append: Selection" + str(selection))
                # print("Random songs: " + str(random_songs))

                for song in random_songs:
                    if str(song['song']) == str(selection['song']):  # if the songs match, mark as duplicate
                        # print("No song appended: " + str(song['song']) + " == " + str(selection['song']))
                        duplicate = True

                if (duplicate == False):
                    # print("Song appended: " + str(song['song']) + " != " + str(selection['song']))
                    random_songs.append(selection)  # append the song if not a duplicate
                    appended = True

                if appended == False:
                    range_num -= 1  # start again
                    duplicate = False

        # seed each of the 5 random songs (rated > 5) to generate recommendations
        urllist = []
        index = 0
        for song in random_songs:
            track_uri = str(song['track_uri'])[14:] + "&"
            artist_uri = str(song['artist_uri'])[15:] + "&"
            index += 1
            seed_artists = artist_uri
            seed_genres = genre + "&"
            seed_tracks = track_uri
            target_acousticness = str(request.form.getlist('values[0][ac_val]'))[2:-2] + "&"
            target_danceability = str(request.form.getlist('values[0][da_val]'))[2:-2] + "&"
            target_energy = str(request.form.getlist('values[0][en_val]'))[2:-2] + "&"
            target_instrumentalness = str(request.form.getlist('values[0][in_val]'))[2:-2] + "&"
            # target_loudness = "0.7&"
            target_popularity = "50&"
            # target_tempo = "110"
            urllist.append("https://api.spotify.com/v1/recommendations?limit=3&market=US&" \
                           "seed_artists=" + seed_artists + \
                           "seed_genres=" + seed_genres + \
                           "seed_tracks=" + seed_tracks + \
                           "target_acousticness=" + target_acousticness + \
                           "target_danceability=" + target_danceability + \
                           "target_energy=" + target_energy + \
                           "target_instrumentalness=" + target_instrumentalness + \
                           "target_popularity=" + target_popularity)
            # "target_loudness=" + target_loudness + \
            # "target_tempo=" + target_tempo

        urllist = str(urllist)[2:-2]
        return urllist


@app.route("/save_rec", methods=['GET', 'POST'])
def save_rec():
    if request.method == 'POST':
        id = str(request.form.getlist('id'))[2:-2]
        track_uri = request.form.getlist('track_uri[]')
        artist_uri = request.form.getlist('artist_uri[]')
        album_cover = request.form.getlist('album_cover[]')
        genre = request.form.getlist('genre[]')

        data = str(request.form.getlist('track_list[]'))[1:-1]  # get the track list
        split = data.split('.,.')
        first = True
        index = 0

        for track in split:
            if track != '\'' and track != '' and track != '\"':
                # print(str(track) + ": Track length: " + str(len(split)) + ", URI: " + str(len(track_uri)))
                if first == False:
                    track = track[4:]
                else:
                    track = track[1:]
                first = False

                if track[-1] == '\'' or track[-1] == '\"':
                    track = track[:-1]

                tr_uri = track_uri[index]
                ar_uri = artist_uri[index]
                gen = genre[index]

                # album cover can be single or []
                if album_cover == []:
                    al_cov = str(request.form.getlist('album_cover'))[2:-2]
                else:
                    al_cov = album_cover[index]

                index += 1
                record = {"user": id, "song": track, "genre": gen, "rating": 0, "track_uri": tr_uri,
                          "artist_uri": ar_uri, "album_cover": str(al_cov)}  # rating = 0 means unrated
                x = col.insert_one(record)  # insert to db
        return 'Sucesss', 200


@app.route("/load_rec", methods=['GET', 'POST'])
def load_rec():
    if request.method == 'POST':
        id = str(request.form.getlist('id'))[2:-2]
        cursor = list(col.find({"user": id}))  # find all entries from this user
        # for each song: add .,. and use this as a split in frontend
        songlist = []
        for song in cursor:
            if song['rating'] == 0:  # if not yet rated...
                song = "<img src=\"" + str(song['album_cover'] + "\"></img> ") + str(song['song']) \
                       + ".,."  # .,. is our split - cannot use ", "
                songlist.append(song)
        songlist = str(songlist)[2:-2]
        return songlist, 200


@app.route("/rate_rec", methods=['GET', 'POST'])
def rate_rec():
    if request.method == 'POST':
        id = str(request.form.getlist('userRating[user]'))[2:-2]
        song = str(request.form.getlist('userRating[song]'))[2:-2]
        rating = str(request.form.getlist('userRating[rating]'))[2:-2]
        result = col.find_one_and_update(
            {"user": id, "song": song},  # find this...
            {"$set": {"rating": rating}})  # set the rating
        return "songlist", 200


@app.route("/get_uris", methods=['GET', 'POST'])
def get_uris():
    track_list = request.form.getlist('track_list[]')
    artist_uris = []
    track_uris = []
    album_covers = []
    for track in track_list:
        artist_uris.append(str(list(col.find({"song": track[:-3]}, {"_id": 0, "artist_uri": 1})))[17:-3])
        track_uris.append(str(list(col.find({"song": track[:-3]}, {"_id": 0, "track_uri": 1})))[16:-3])
        album_covers.append(str(list(col.find({"song": track[:-3]}, {"_id": 0, "album_cover": 1})))[18:-3])

    uris = [str(artist_uris) + ".,.", str(track_uris) + ".,.", str(album_covers)]

    return str(uris)


@app.route('/get_genres', methods=['GET', 'POST'])
def get_genres():
    genres = []
    track_list = request.form.getlist('track_list[]')
    for track in track_list:
        cursor = list(col.find({"song": track[:-3]}))  # find all entries from this user
        for item in cursor:
            genres.append(item['genre'])

    res = str(genres)
    return res


@app.route('/access_token', methods=['GET', 'POST'])
def access_token():
    global access_token
    # GET request
    if request.method == 'GET':
        with open('token.txt') as json_file:  # read the file...
            data = json.load(json_file)
            for p in data['token']:
                # print('Token: ' + p['acs_tkn'])
                access_token = p['acs_tkn']

        return str(access_token)  # give the access token

    # POST request
    if request.method == 'POST':
        access_token = str(request.form)  # take the response and cut out the token
        access_token = str(request.form.getlist('str_ac_tk'))[2:-2]
        # print(access_token)

        data = {'token': []}  # convert to json...
        data['token'].append({
            'acs_tkn': access_token
        })

        with open('token.txt', 'w') as outfile:  # write to file...
            json.dump(data, outfile)

        return "Successfully saved.", 200


@app.route('/ml_recommend', methods=['POST'])
def recommend():
    id = str(request.form.getlist('id'))[2:-2]
    user_num = 0

    csv_export = {'self_index': [], 'user_id': [], 'song_id': [], 'rating': []}  # write to csv

    distinct_songs = col.distinct("song")  # get all songs and give them IDs...
    distinct_users = col.distinct("user")  # get all users and give them IDs...

    songlist = {'song_id': [], 'song_name': [], 'song_genre': []}
    userlist = {'user_id': [], 'user_name': []}
    ratinglist = {'user_id': [], 'song_id': [], 'song_name': [], 'rating': []}

    for song in distinct_songs:
        songlist['song_name'].append(song)
        songlist['song_id'].append(songlist['song_name'].index(song) + 1)
        gen = col.find({"song": song})
        songlist['song_genre'].append(gen[0]['genre'])


    for user in distinct_users:
        userlist['user_name'].append(user)
        userlist['user_id'].append(userlist['user_name'].index(user) + 1)
        if user == id:
            user_num = userlist['user_name'].index(user) + 1

    # we currently have a list of every song and user with ids

    ratinglist['user_id'] = userlist['user_id']
    ratinglist['song_id'] = songlist['song_id']

    index = 0
    for user in userlist['user_name']:  # every user
        cursor = list(col.find({"user": user}))  # find all entries from each user
        for song in songlist['song_name']:  # every song
            for user_song in cursor:
                if song == user_song['song']:  # if the user has been recommended this song...
                    ratinglist['rating'].append(user_song['rating'])
                    csv_export['self_index'].append(index)
                    csv_export['user_id'].append(userlist['user_name'].index(user) + 1)
                    csv_export['song_id'].append(songlist['song_name'].index(song) + 1)
                    csv_export['rating'].append(float((user_song['rating'])))
                    index += 1

    with open("ratings.csv", 'w', newline='') as myfile:
        wr = csv.writer(myfile)
        wr.writerow(["user_id", "song_id", "rating", "timestamp"])
        for num in csv_export['self_index']:
            row = [csv_export['user_id'][num],
                   csv_export['song_id'][num],
                   csv_export['rating'][num],
                   964982703]
            wr.writerow(row)

    with open("songs.csv", 'w', newline='') as myfile:
        wr = csv.writer(myfile)
        wr.writerow(["song_id", "song_name", "genre"])
        for song in songlist['song_id']:
            row = [str(songlist['song_id'][song - 1]),
                   str(songlist['song_name'][song - 1]),
                   str(songlist['song_genre'][song - 1])]
            wr.writerow(row)

    res = gen_rec(user_num)

    return str(res)[2:-5]


if __name__ == "__main__":
    app.run(host="localhost", port=8080, debug=False)
