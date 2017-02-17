import json
import re
import urllib
import urllib.request
import config

from bs4 import BeautifulSoup
from flask import Flask

app = Flask(__name__)
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
        return "Exception occurred \n" + str(e)


@app.route('/')
def hello_world():
    return "Hello World"


@app.route('/user/<username>')
def display_lyrics(username):
    url = 'https://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&api_key={}&limit=1&format=json&user={}'\
        .format(lastfm_api_key, username)
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())
    recent_track = data['recenttracks']['track'][0]
    try:
        now_playing = recent_track['@attr']['nowplaying']
        if now_playing == 'true':
            recent_track_title = recent_track['name']
            recent_track_artist = recent_track['artist']['#text']

            lyrics = get_lyrics(recent_track_artist, recent_track_title)

            body = '<div>'
            body += '</br>'.join(lyrics.split('\n'))
            body += '</div>'
            return body

    except KeyError:
        return "You don't appear to be scrobbling right now."

    return "This should not happen"


if __name__ == '__main__':
    app.run(debug=False)
