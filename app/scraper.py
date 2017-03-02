import requests
from bs4 import BeautifulSoup
import config

base_url = "http://api.genius.com"
headers = {'Authorization': config.GENIUS_BEARER_TOKEN}


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
    print(artist_name)
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
