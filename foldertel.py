import os
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
    folder_path = f"{artist_name}/{album_name}"
    
    try:
        os.makedirs(folder_path)
        user_id = context.bot_data["user_id"]
        context.bot.send_message(chat_id=user_id, text=f"Folder created successfully: {folder_path}")
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
