# -*- coding: utf-8 -*-
from surprise import KNNBasic
from surprise import Dataset
from surprise import Reader

from collections import defaultdict
from operator import itemgetter
import heapq

import csv


def load_dataset():
    reader = Reader(line_format='user item rating timestamp', sep=',', skip_lines=1)
    ratings_dataset = Dataset.load_from_file('ratings.csv', reader=reader)

    song_id_to_name = {}
    with open('songs.csv', newline='', encoding='ISO-8859-1') as csvfile:
        song_reader = csv.reader(csvfile)
        next(song_reader)
        for row in song_reader:
            song_id = int(row[0])
            song_name = row[1]
            song_id_to_name[song_id] = song_name
    # Return both the dataset and lookup dict in tuple
    return ratings_dataset, song_id_to_name


def get_song_name(song_id, song_id_to_name):
    if int(song_id) in song_id_to_name:
        return song_id_to_name[int(song_id)]
    else:
        return ""


def gen_rec(user_num):
    dataset, song_id_to_name = load_dataset()

    # Build a full Surprise training set from dataset
    trainset = dataset.build_full_trainset()

    similarity_matrix = KNNBasic(sim_options={
        'name': 'cosine',
        'user_based': False
    }) \
        .fit(trainset) \
        .compute_similarities()

    # Current user
    test_subject = str(user_num)

    # Get the top K items user rated
    k = 20

    test_subject_iid = trainset.to_inner_uid(test_subject)

    # Top items rated by ML
    test_subject_ratings = trainset.ur[test_subject_iid]    # ur = user ratings, supplied with id
    k_neighbors = heapq.nlargest(k, test_subject_ratings, key=lambda t: t[1])   # sorted list of top 20 rated items

    candidates = defaultdict(float)

    for itemID, rating in k_neighbors:  # starts with highest ratings and goes through list
        try:
            similarities = similarity_matrix[itemID]    # find most similar item to itemID in matrix
            for innerID, score in enumerate(similarities):  # for each similar item, add to candidate
                candidates[innerID] += score * (rating / 5.0)
        except:
            continue

    # Build a dictionary of songs the user has listened to
    watched = {}
    for itemID, rating in trainset.ur[test_subject_iid]:
        watched[itemID] = 1

    recommendations = []

    position = 0
    for itemID, rating_sum in sorted(candidates.items(), key=itemgetter(1), reverse=True):  # similar songs
        if not itemID in watched:   # if the user hasn't listened
            recommendations.append(get_song_name(trainset.to_raw_iid(itemID), song_id_to_name))
            position += 1
            if position > 10:
                break  # We only want top 10

    rec_list = []
    for rec in recommendations:
        rec_list.append(rec + ".,.")

    return rec_list
