from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, disconnect

from api_functions import get_lyrics, fetch_lastfm_music_data

async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None


def user_is_currently_scrobbling():
    return True


def background_thread(args):
    username = args[0]
    last_song = {}
    while True:
        music_data = fetch_lastfm_music_data(username)
        print(music_data)
        if type(music_data) == KeyError:
            if music_data.args[0] == 'recenttracks':
                print('no such user')
                socketio.emit('no_user', namespace='/lyrics')
            if music_data.args[0] == '@attr':
                print('not scrobbling')
                socketio.emit('not_scrobbling', namespace='/lyrics')
                socketio.sleep(10)
                continue
        current_song = {music_data['artist'], music_data['title']}
        if current_song != last_song:
            if type(music_data) == dict:
                payload = music_data
                payload['lyrics'] = get_lyrics(music_data['artist'], music_data['title'])
                socketio.emit('json', payload, namespace='/lyrics')
        last_song = current_song
        socketio.sleep(10)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/user/<username>')
def show_lyrics(username):
    return render_template('lyrics.html')


@socketio.on('disconnect_request', namespace='/lyrics')
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']})
    disconnect()


@socketio.on('connect', namespace='/lyrics')
def test_connect():
    emit('my_response', {'data': 'Connected', 'count': 0})


@socketio.on('send_username', namespace='/lyrics')
def start_thread(message):
    username = message['data']
    print(username)
    global thread
    if thread is None:
        thread = socketio.start_background_task(target=background_thread, args=(username,))


@socketio.on('disconnect', namespace='/lyrics')
def test_disconnect():
    print('Client disconnected', request.sid)


if __name__ == '__main__':
    socketio.run(app, debug=True)
