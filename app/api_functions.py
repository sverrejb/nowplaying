import requests
from bs4 import BeautifulSoup
import config

import json
import urllib
import urllib.request


base_url = "http://api.genius.com"
headers = {'Authorization': config.GENIUS_BEARER_TOKEN}


def fetch_lastfm_music_data(username):
    url = 'https://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&api_key={}&limit=1&format=json&user={}' \
        .format(config.LASTFM_API_KEY, username)
    print(url)
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())
    print(data)

    try:
        recent_track = data['recenttracks']['track'][0]
        now_playing = recent_track['@attr']['nowplaying']
        if now_playing == 'true':
            print("works")
            recent_track_title = recent_track['name']
            recent_track_artist = recent_track['artist']['#text']
            image = recent_track['image'][-1]['#text']
            return str({'artist': recent_track_artist, 'title': recent_track_title, 'image': image})

    except KeyError as e:
        return e


def lyrics_from_song_api_path(song_api_path):
    song_url = base_url + song_api_path
    response = requests.get(song_url, headers=headers)
    json = response.json()
    path = json["response"]["song"]["path"]
    page_url = "http://genius.com" + path
    page = requests.get(page_url)
    html = BeautifulSoup(page.text, "html.parser")
    [h.extract() for h in html('script')]
    lyrics = html.find("lyrics").get_text()
    return lyrics


def get_lyrics(artist_name, song_title):
    artist_name = artist_name.replace(' & ', ' and ')
    song_title = song_title.replace('&', '\&')
    search_url = base_url + "/search?q=" + song_title
    response = requests.get(search_url, headers=headers)
    json = response.json()
    song_info = None
    for hit in json["response"]["hits"]:
        if hit["result"]["primary_artist"]["name"] == artist_name:
            song_info = hit
            break
    if song_info:
        song_api_path = song_info["result"]["api_path"]
        lyrics = lyrics_from_song_api_path(song_api_path)
        return lyrics
    else:
        return "Sorry, no lyrics found :("
