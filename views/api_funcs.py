import requests
import random
import base64
import urllib
from secret import IMG_CLIENT_ID, IMG_API_KEY, SPOTIFY_CLIENT_ID, SPOTIFY_API_KEY
###############################################################
# AI IMAGE API REQUEST FUNCTIONS

IMG_API_BASE_URL = 'https://api.everypixel.com/v1/keywords'
def get_keywords(image_path):
    """Gets keywords from AI image keywording API 
    and returns them as a list"""

    with open(image_path, 'rb') as image:
        data = {'data': image}
        params = {'num_keywords': 5}
        json_resp = requests.post(IMG_API_BASE_URL,
                                 files=data,
                                 params=params,
                                 auth=(IMG_CLIENT_ID, IMG_API_KEY)).json()
        if (json_resp['status'] == 'ok'):
            keywords_resp = json_resp['keywords']
            keywords = [keyword_obj['keyword'] for keyword_obj in keywords_resp]
            return keywords
        return None
    

###############################################################
# SPOTIFY REQUEST FUNCTIONS

def get_spotify_token():
    """Get access token to make requests to Spotify API 
    Resource tutorial used: https://www.youtube.com/watch?v=WAmEZBEeNmg
    """

    auth_string = SPOTIFY_CLIENT_ID + ':' + SPOTIFY_API_KEY
    #encoded auth_string
    auth_bytes = auth_string.encode('utf-8')
    #encode with base64
    auth_base64 = str(base64.b64encode(auth_bytes), 'utf-8')
    #send post request to Spotify OAuth Service
    url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Authorization': 'Basic ' + auth_base64,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'client_credentials'
    }
    result = requests.post(url, headers=headers, data=data)
    json_result = result.json()
    token = json_result['access_token']
    return token


SPOTIFY_SEARCH_BASE_URL = 'https://api.spotify.com/v1/search'
def get_track_data(track_keyword):
    """Makes GET request to Spotify search endpoint and returns data in object
    Resource Tutorial used: https://www.youtube.com/watch?v=uXf7IRDIQS4"""

    # Randomize offset where search response list begins
    rand_offset = random.randint(0, 150)

    # Parse keywords to be url-compatible
    search_keyword = urllib.parse.quote(f'%{track_keyword}%')
    query = f'?q={search_keyword}&type=track&limit=1&offset={rand_offset}'
    query_url = SPOTIFY_SEARCH_BASE_URL + query

    # Grab token
    token = get_spotify_token()

    # Add token to header
    headers = {'Authorization': 'Bearer ' + token}

    # Send request to API and dissect response
    resp = requests.get(query_url, headers=headers)
    resp_json = resp.json()
    tracks = resp_json['tracks']['items']
    
    for track in tracks:
        title = track['name']
        album = track['album']['name']
        album_year = track['album']['release_date'][:4]
        artists = ', '.join([artist['name'] for artist in track['artists']])
        spotify_track_id = track['id']
        spotify_url = track['external_urls']['spotify']
        image_url = track['album']['images'][0]['url']
        audio_url = track['preview_url']

        return{
            'title': title,
            'album': album, 
            'album_year': album_year,
            'artists': artists,
            'spotify_track_id': spotify_track_id,
            'spotify_url': spotify_url,
            'image_url': image_url,
            'audio_url': audio_url
        }


def get_list_of_tracks(keywords):
    """Returns a list of all song-objects"""

    return [get_track_data(keyword) for keyword in keywords]

