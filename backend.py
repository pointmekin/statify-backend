# from flask_ngrok import run_with_ngrok
from flask import Flask
from flask import request
from flask import jsonify
from flask import send_file, make_response
from pymongo import MongoClient
from flask_cors import CORS, cross_origin


import os

app = Flask(__name__)
CORS(app, support_credentials=True)
# run_with_ngrok(app)

client = MongoClient(
    "mongodb+srv://testuser:mongotestuserpassword@cluster0.li4tz.mongodb.net/Cluster0?retryWrites=true&w=majority")
db = client.test

# home page


@app.route('/')
def home():
    return '<h1>Statify</h1>'

# inserting test data (temporary)


@app.route('/add_test_data')
def addTestData():
    for model in model_list:
        db.test_data.insert_one(model)
    return('<h3>Finished Adding</h3>')

# adding all data


@app.route('/add_data')
def addData():
    for model in model_list:
        db.music_data.insert_one(model)
    return('<h3>Finished Adding All Data</h3>')

# adding overall statistics


@app.route('/add_overall_statistics')
def add_overall_statistics():
    db.overall_statistics.insert_one(overall_statistics())
    return('<h3>Finished Adding Overall Statistics</h3>')


@app.route('/get')
def get():
    ret = dict()
    name = str(request.args.get('name'))
    ret = db.music_data.find(
        {'name': {"$regex": name, '$options': 'i'}}).limit(20)

    docs = []
    for doc in ret:
        del doc['_id']
        docs.append(doc)
        print(doc)

    print(docs)
    return jsonify(docs)

# In the final version (after adding song id, search with songid instead)


@app.route('/get_details')
def get_details():
    ret = dict()
    id = str(request.args.get('id'))
    ret = db.music_data.find_one({'name': id})
    del ret['_id']
    print(ret)
    return jsonify(ret)


@app.route('/get_popular')
def get_popular():
    ret = dict()
    popularity = int(request.args.get('popularity'))

    ret = db.music_data.find({"popularity": {"$lt": popularity}}).sort(
        [('popularity', -1)]).limit(20)

    docs = []
    for doc in ret:
        del doc['_id']
        docs.append(doc)
        print(doc)

    print(docs)
    return jsonify(docs)


# @app.route('/plot', methods=['GET'])
# def plot():

#     info1 = dict()
#     id = str(request.args.get('song_id1'))
#     info1 = db.music_data.find_one({'name': {"$regex": id, '$options': 'i'}})

#     info2 = dict()
#     id = str(request.args.get('song_id2'))
#     info2 = db.music_data.find_one({'name': {"$regex": id, '$options': 'i'}})

#     bytes_obj = do_plot(info1, info2)

#     return (send_file(bytes_obj,
#                       attachment_filename='plot.png',
#                       mimetype='image/png'))


@app.route('/compare', methods=['GET'])
def compare():

    info1 = dict()
    id = str(request.args.get('song_id1'))
    info1 = db.music_data.find_one({'name': {"$regex": id, '$options': 'i'}})
    del info1['_id']

    info2 = dict()
    id = str(request.args.get('song_id2'))
    info2 = db.music_data.find_one({'name': {"$regex": id, '$options': 'i'}})
    del info2['_id']
    combined = [
        info1,
        info2
    ]

    return jsonify(combined)


@app.route('/create_playlist')
def createPlaylist():
    playlist_name = str(request.args.get('playlist_name'))
    model = {
        'playlist_name': playlist_name,
        'count': 0,
        'music': []
    }
    db.public_playlist.insert_one(model)
    return('<h3>Finished Adding</h3>')


@app.route('/add_to_playlist')
def add_to_playlist():
    playlist_name = str(request.args.get('playlist_name'))
    song_id = str(request.args.get('song_id'))

    db.public_playlist.update(
        {'playlist_name': playlist_name},
        {'$addToSet': {"music": song_id}}
    )
    return('<h3>Finished Adding</h3>')


@app.route('/get_playlist')
def get_playlist():
    playlist_name = str(request.args.get('playlist_name'))

    list_of_songs = []
    all_songs = []
    ret = db.public_playlist.find_one({'playlist_name': playlist_name})
    del ret['_id']

    all_songs = ret['music']
    print("ALL SONGS ARE: ", all_songs)

    for i in range(len(all_songs)):
        id = all_songs[i]
        ret = db.music_data.find_one({'id': id})
        del ret['_id']
        print("song result:", ret)
        list_of_songs.append(ret)

    return jsonify(list_of_songs)


@app.route('/all_playlists')
def get_all_playlists():
    ret = db.public_playlist.find({})

    docs = []
    for doc in ret:
        del doc['_id']
        docs.append(doc)
        print(doc)

    print(docs)
    return jsonify(docs)


app.run()
