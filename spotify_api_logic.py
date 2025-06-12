from requests import get
from auth import get_auth_header
import json

# function to search for artist
def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1" # gives most popular artist

    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["artists"]["items"]
    if len(json_result) == 0:
        print("No artist with this name exists...")
        return None
    
    return json_result[0]

def get_artist_name(token, artist_name):
    artist_result = search_for_artist(token, artist_name)
    name = artist_result['name']

    return name

# function to get songs from artist
def get_artists_top_tracks(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=CA" # look for specific artist and their top tracks
    headers = get_auth_header(token)
    result = get(url, headers=headers)

    try:
        data = json.loads(result.content)
        return data["tracks"]
    except (json.JSONDecodeError, KeyError) as e:
        print("Spotify API error:", result.status_code)
        print("Response content:", result.content)
        return []  # Return empty list so your app/test doesn’t crash

    # json_result = json.loads(result.content)["tracks"]
    # return json_result 

def get_artists_top_tracks_string(token, artist_id):
    top_tracks = get_artists_top_tracks(token, artist_id)
    names = [track["name"] for track in top_tracks[:10]]
    return ", ".join(names)

# function to get albums from specific artist
def get_artists_albums(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/albums?include_groups=album&limit=50" # request for artist's albums, limit to 50 items returned
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["items"]
    return json_result

def get_artists_albums_ids(token, artist_id):
    albums = get_artists_albums(token, artist_id)
    album_ids = []

    for idx, album in enumerate(albums):
        # print(f"{idx + 1}, ID: {album['id']}")
        album_ids.append(album['id'])
    
    return album_ids

def get_num_artist_albums(token, artist_id):
    albums = get_artists_albums(token, artist_id)
    counter = 0

    for idx, album in enumerate(albums):
        counter += 1
    
    return counter

def get_artists_top_tracks_popularity(token, artist_id):
    top_tracks = get_artists_top_tracks(token, artist_id)
    pop_score = []

    for idx, song in enumerate(top_tracks):
        # print(f"{idx + 1}, {song['name']} has a popularity score of {song['popularity']}")
        pop_score.append(song['popularity']) # stores popularity score of top 10 tracks into an array
    
    return pop_score

def print_top_tracks_and_popularity(token, artist_id):
    top_tracks = get_artists_top_tracks(token, artist_id)

    for idx, track in enumerate(top_tracks):
        print(f"{idx +1}. {track['name']} has a popularity score of {track['popularity']}")

def get_album_tracks(token, artist_id):
    album_ids = get_artists_albums_ids(token, artist_id)
    track_names = []
    headers = get_auth_header(token)
    for idx, album_id in enumerate(album_ids):
        url = f"https://api.spotify.com/v1/albums/{album_id}/tracks"
        result = get(url, headers=headers)
        album_items = json.loads(result.content)["items"] # get items of each album

        for idx, album_item in enumerate(album_items):
            track_names.append(album_item['name'])
    
    return track_names

def get_avg_pop_score(token, artist_id):
    pop_array = get_artists_top_tracks_popularity(token, artist_id)
    total = 0
    for i in pop_array:
        total += i
    
    avg_pop = total / len(pop_array)

    return avg_pop

def get_user(token):
    url = "https://api.spotify.com/v1/me"
    headers = get_auth_header(token)

    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    return json_result
