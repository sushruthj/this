import os
import subprocess
import shutil
import time
import telebot
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pycdlib import PyCdlib
from pydub import AudioSegment
from mutagen.easyid3 import EasyID3
import musicbrainzngs

# Function to read bot token and user ID from a text file
def read_config(filename):
    config = {}
    with open(filename, 'r') as file:
        for line in file:
            key, value = line.strip().split('=')
            config[key] = value
    return config

# Read bot token and user ID from config file
config = read_config('config.txt')
BOT_TOKEN = config.get('BOT_TOKEN')
YOUR_TELEGRAM_USER_ID = config.get('USER_ID')

# Path to the directory where FLAC files will be saved
output_folder = "/path/to/output/folder"

# MusicBrainz API setup
musicbrainzngs.set_useragent("RipCDBot", "1.0", "YOUR_EMAIL_ADDRESS")

class AudioCDHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            drive_path = event.src_path
            self.ask_for_album_name(drive_path)

    def ask_for_album_name(self, drive_path):
        if YOUR_TELEGRAM_USER_ID:
            bot = telebot.TeleBot(BOT_TOKEN)
            bot.send_message(YOUR_TELEGRAM_USER_ID, "Please enter the album name:")
            user_album_mapping[YOUR_TELEGRAM_USER_ID] = drive_path

    def on_deleted(self, event):
        if event.is_directory:
            drive_path = event.src_path
            self.cleanup_files(drive_path)

    def rip_audio_cd(self, drive_path, album_name):
        # Create output folder if it doesn't exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Use pycdlib to read the CD contents
        with PyCdlib() as c:
            c.open(drive_path)
            tracks = c.list_tracks()

            # Extract each track as FLAC file
            for track in tracks:
                track_number = int(track.split('/')[0])
                track_filename = os.path.join(output_folder, f"track{track_number}.wav")
                c.extract(track, track_filename)

                # Convert WAV to FLAC using pydub
                audio = AudioSegment.from_wav(track_filename)
                flac_filename = os.path.join(output_folder, f"track{track_number}.flac")
                audio.export(flac_filename, format="flac")

                # Fetch metadata from MusicBrainz and write to file
                self.write_metadata(flac_filename, album_name)

    def cleanup_files(self, drive_path):
        # Remove FLAC files when CD is removed
        for file in os.listdir(output_folder):
            if file.endswith(".flac"):
                os.remove(os.path.join(output_folder, file))

    def write_metadata(self, flac_filename, album_name):
        # Fetch metadata from MusicBrainz
        results = musicbrainzngs.search_releases(query=album_name)
        if "release-list" in results:
            releases = results["release-list"]
            if releases:
                release_id = releases[0]["id"]  # Get the first release ID
                metadata = musicbrainzngs.get_release_by_id(release_id, includes=["artists", "recordings", "labels"])
                if "release" in metadata:
                    release = metadata["release"]
                    artists = [artist["name"] for artist in release["artist-credit"]]
                    title = release["title"]
                    date = release["date"]
                    tracks = release["medium-list"][0]["track-list"]
                    track_titles = [track["recording"]["title"] for track in tracks]
                    track_artists = [", ".join([artist["name"] for artist in track["recording"]["artist-credit"]]) for track in tracks]

                    # Write metadata to FLAC file
                    audio = EasyID3(flac_filename)
                    audio["artist"] = artists
                    audio["album"] = title
                    audio["date"] = date
                    for i, (track_title, track_artist) in enumerate(zip(track_titles, track_artists)):
                        audio[f"title{i + 1}"] = track_title
                        audio[f"artist{i + 1}"] = track_artist
                    audio.save()

def start_telegram_listener(event_handler):
    bot = telebot.TeleBot(BOT_TOKEN)

    @bot.message_handler(func=lambda message: True)
    def handle_message(message):
        user_id = message.chat.id
        if user_id in user_album_mapping:
            album_name = message.text
            drive_path = user_album_mapping[user_id]
            event_handler.rip_audio_cd(drive_path, album_name)
            del user_album_mapping[user_id]
            bot.send_message(user_id, "CD ripping completed successfully!")
        else:
            bot.send_message(user_id, "Invalid command.")

    bot.polling()

if __name__ == "__main__":
    # Start Telegram listener in a separate thread
    import threading
    user_album_mapping = {}
    event_handler = AudioCDHandler()
    telegram_thread = threading.Thread(target=start_telegram_listener, args=(event_handler,))
    telegram_thread.daemon = True
    telegram_thread