import os
import subprocess
from os.path import expanduser
from telegram import Update
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters, CallbackContext
ALBUM, ARTIST = range(2)


def start(update: Update, context: CallbackContext):
    user_id = context.bot_data["user_id"]
    context.bot.send_message(chat_id=user_id, text="Please enter the album name.")
    return ALBUM


def album(update: Update, context: CallbackContext):
    context.user_data['album'] = update.message.text
    user_id = context.bot_data["user_id"]
    context.bot.send_message(chat_id=user_id, text="Great! Now enter the artist name.")
    return ARTIST


def artist(update: Update, context: CallbackContext):
    artist_name = update.message.text
    album_name = context.user_data['album']
    home_dir = expanduser("~")
    with open('sec.txt', 'r') as file:
         password = file.read().strip()
    command = ['sudo', '-S', 'mount', '/dev/sda1']  
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    stdout, stderr = process.communicate(input=password+'\n')
    mediapath="/mnt/SanDisk"
    #folder_path = os.path.join(mediapath, artist_name, album_name)
    midpath = "Music"
    
    folder_path = os.path.join(mediapath, midpath, artist_name, album_name)

    try:
        os.makedirs(folder_path)
        user_id = context.bot_data["user_id"]
        context.bot.send_message(chat_id=user_id, text=f"Folder created successfully: {folder_path}")
        os.chdir(folder_path)

        # Create a file named "success.txt"
        subprocess.run(["cdparanoia", "-B"])
        bash_script_content = '''#!/bin/bash
                              for i in *.wav; do
                                  ffmpeg -i "$i" -c:a flac "${i%\.*}.flac";
                              done 
                              '''

        with open("convert_to_flac.sh", "w") as file:
            file.write(bash_script_content)
        subprocess.run(["chmod", "+x", "convert_to_flac.sh"])
        subprocess.run(["./convert_to_flac.sh"])
        subprocess.run(["rm", "*.wav"])
        subprocess.run(["rm", "*.sh"])

        # Notify the user
        context.bot.send_message(chat_id=user_id, text="CD Ripped.")
    except OSError as e:
        user_id = context.bot_data["user_id"]
        context.bot.send_message(chat_id=user_id, text=f"Folder creation failed: {str(e)}")
    return ConversationHandler.END
def load_config(file_path):
    bot_token = ""
    user_id = ""
    with open(file_path, "r") as file:
        lines = file.readlines()
        for line in lines:
            key, value = line.strip().split("=")
            if key == "bot_token":
                bot_token = value
            elif key == "user_id":
                user_id = value
    return bot_token, user_id
def main():
    config_file = "config.txt"
    bot_token, user_id = load_config(config_file)
    updater = Updater(bot_token)
    updater.dispatcher.bot_data["user_id"] = user_id
    updater.dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ALBUM: [MessageHandler(Filters.text, album)],
            ARTIST: [MessageHandler(Filters.text, artist)]
        },
        fallbacks=[]
    ))
    updater.start_polling()
    updater.idle()
if __name__ == '__main__':
    main()
