import json
import re
import urllib
import urllib.request

from bs4 import BeautifulSoup
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, disconnect


import config

async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None

lastfm_api_key = config.LASTFM_API_KEY


# TEMP method for testing purposes
def get_lyrics(artist, song_title):
    artist = artist.lower()
    song_title = song_title.lower()
    # remove all except alphanumeric characters from artist and song_title
    artist = re.sub('[^A-Za-z0-9]+', "", artist)
    song_title = re.sub('[^A-Za-z0-9]+', "", song_title)
    if artist.startswith("the"):  # remove starting 'the' from artist e.g. the who -> who
        artist = artist[3:]
    url = "http://azlyrics.com/lyrics/" + artist + "/" + song_title + ".html"

    try:
        content = urllib.request.urlopen(url).read()
        soup = BeautifulSoup(content, 'html.parser')
        lyrics = str(soup)
        # lyrics lies between up_partition and down_partition
        up_partition = '<!-- Usage of azlyrics.com content by any third-party lyrics provider is prohibited by our licensing agreement. Sorry about that. -->'
        down_partition = '<!-- MxM banner -->'
        lyrics = lyrics.split(up_partition)[1]
        lyrics = lyrics.split(down_partition)[0]
        lyrics = lyrics.replace('<br>', '').replace('</br>', '').replace('</div>', '').strip()
        return lyrics
    except Exception as e:
        return "Sorry, no lyrics found :(\n" + str(e)


def background_thread():
    count = 0
    while True:
        socketio.sleep(10)
        count += 1
        print('emitting')
        socketio.emit('json',
                      {'data': 'Server generated event', 'count': count},
                      namespace='/test')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/user/<username>')
def lyrics(username):
    url = 'https://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&api_key={}&limit=1&format=json&user={}' \
        .format(lastfm_api_key, username)
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())
    recent_track = data['recenttracks']['track'][0]
    try:
        now_playing = recent_track['@attr']['nowplaying']
        if now_playing == 'true':
            recent_track_title = recent_track['name']
            recent_track_artist = recent_track['artist']['#text']
            image = recent_track['image'][-1]['#text']
            lyrics = get_lyrics(recent_track_artist, recent_track_title).split('\n')

            return render_template('lyrics.html', lyrics=lyrics, title=recent_track_title,
                                   image=image, artist=recent_track_artist)

    except KeyError: # TODO: FIX THIS
        return render_template('not_scrobbling.html')

    return "This should not happen"


@socketio.on('my_event', namespace='/test')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']})


@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']})
    disconnect()


@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    print("connected")
    if thread is None:
        thread = socketio.start_background_task(target=background_thread)
    emit('my_response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)


if __name__ == '__main__':
    socketio.run(app, debug=True)
