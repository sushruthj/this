import os
import subprocess
import sys
import venv
import time
import telebot
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pycdlib import PyCdlib
from pydub import AudioSegment
from mutagen.easyid3 import EasyID3

# Function to install required Python libraries using pip
def install_libraries():
    libraries = ['telebot', 'watchdog', 'pycdlib', 'pydub', 'mutagen']
    subprocess.check_call([sys.executable, "-m", "pip", "install"] + libraries)

# Function to create and activate virtual environment
def create_and_activate_venv():
    venv_dir = 'venv'
    if not os.path.exists(venv_dir):
        venv.create(venv_dir, with_pip=True)
    activate_script = os.path.join(venv_dir, 'Scripts' if os.name == 'nt' else 'bin', 'activate')
    subprocess.check_call([activate_script], shell=True)

# Install required libraries
create_and_activate_venv()
install_libraries()

# Read bot token and user ID from config file
def read_config(filename):
    config = {}
    with open(filename, 'r') as file:
        for line in file:
            key, value = line.strip().split('=')
            config[key] = value
    return config

# Path to the directory where FLAC files will be saved
output_folder = "/path/to/output/folder"

class AudioCDHandler(FileSystemEventHandler):
    def __init__(self, bot_token, user_id):
        self.bot_token = bot_token
        self.user_id = user_id
        self.user_album_mapping = {}

    def on_created(self, event):
        if event.is_directory:
            drive_path = event.src_path
            self.ask_for_album_name(drive_path)

    def ask_for_album_name(self, drive_path):
        if self.user_id:
            bot = telebot.TeleBot(self.bot_token)
            bot.send_message(self.user_id, "Please enter the album name:")
            self.user_album_mapping[self.user_id] = drive_path

    def on_deleted(self, event):
        if event.is_directory:
            drive_path = event.src_path
            self.cleanup_files(drive_path)

    def rip_audio_cd(self, drive_path, album_name):
        # Create output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)

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

    def cleanup_files(self, drive_path):
        # Remove FLAC files when CD is removed
        for file in os.listdir(output_folder):
            if file.endswith(".flac"):
                os.remove(os.path.join(output_folder, file))

def start_telegram_listener(event_handler):
    bot = telebot.TeleBot(event_handler.bot_token)

    @bot.message_handler(func=lambda message: True)
    def handle_message(message):
        user_id = message.chat.id
        if user_id in event_handler.user_album_mapping:
            album_name = message.text
            drive_path = event_handler.user_album_mapping[user_id]
            event_handler.rip_audio_cd(drive_path, album_name)
            del event_handler.user_album_mapping[user_id]
            bot.send_message(user_id, "CD ripping completed successfully!")
        else:
            bot.send_message(user_id, "Invalid command.")

    bot.polling()

if __name__ == "__main__":
    # Read bot token and user ID from config file
    config = read_config('config.txt')
    BOT_TOKEN = config.get('BOT_TOKEN')
    YOUR_TELEGRAM_USER_ID = config.get('USER_ID')

    # Start Telegram listener in a separate thread
    import threading
    event_handler = AudioCDHandler(BOT_TOKEN, YOUR_TELEGRAM_USER_ID)
    telegram_thread = threading.Thread(target=start_telegram_listener, args=(event_handler,))
    telegram_thread.daemon = True
    telegram_thread.start()

    # Specify the path to monitor for CD events (e.g., /Volumes on macOS)
    path_to_monitor = "/path/to/monitor"

    observer = Observer()
    observer.schedule(event_handler, path_to_monitor, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

