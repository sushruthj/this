import os
import urllib.parse
import urllib.request
import json

# Function to fetch track names from the MusicBrainz API
def fetch_track_names(artist, album):
    # Encode artist and album names for URL
    encoded_artist = urllib.parse.quote(artist)
    encoded_album = urllib.parse.quote(album)

    # Create the URL to fetch track names
    url = f"https://musicbrainz.org/ws/2/release/?query=artist:{encoded_artist}%20AND%20release:{encoded_album}&fmt=json"

    try:
        # Fetch track names from the MusicBrainz API
        response = urllib.request.urlopen(url)
        data = json.load(response)

        # Parse the JSON response to get track names
        if 'releases' in data:
            for release in data['releases']:
                if 'media' in release:
                    for media in release['media']:
                        if 'tracks' in media:
                            track_names = []
                            for track in media['tracks']:
                                if 'title' in track:
                                    track_names.append(track['title'])
                            return track_names

        return None

    except:
        print(f"Error fetching track names for {artist}/{album}")
        return None

# Base directory where your music is stored
base_dir = "/home/jay/Everything/Music"

# Loop through all directories and files in the base directory
for artist_name in os.listdir(base_dir):
    artist_dir = os.path.join(base_dir, artist_name)
    if os.path.isdir(artist_dir):
        for album_name in os.listdir(artist_dir):
            album_dir = os.path.join(artist_dir, album_name)
            if os.path.isdir(album_dir):
                # Fetch track names for the current album
                track_names = fetch_track_names(artist_name, album_name)

                # Create a text file to store the track list
                track_list_path = os.path.join(album_dir, "track_list.txt")
                with open(track_list_path, "w") as file:
                    if track_names:
                        # Write track names to the text file
                        for track_name in track_names:
                            file.write(track_name + "\n")
                        print(f"Track list created for {artist_name}/{album_name}")
                    else:
                        print(f"Failed to create track list for {artist_name}/{album_name}")
