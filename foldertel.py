import os
from os.path import expanduser
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters, CallbackContext

ALBUM, ARTIST = range(2)

def start(update: Update, context: CallbackContext):
    if 'album' not in context.user_data:
        user_id = context.bot_data["user_id"]
        context.bot.send_message(chat_id=user_id, text="Please enter the album name.")
        return ALBUM
    else:
        return artist(update, context)

def album(update: Update, context: CallbackContext):
    context.user_data['album'] = update.message.text
    user_id = context.bot_data["user_id"]
    context.bot.send_message(chat_id=user_id, text="Great! Now enter the artist name.")
    return ARTIST

def artist(update: Update, context: CallbackContext):
    artist_name = update.message.text
    album_name = context.user_data['album']
    home_dir = expanduser("~")
    folder_path = os.path.join(home_dir, artist_name, album_name)
    
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

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ALBUM: [MessageHandler(Filters.text, album)],
            ARTIST: [MessageHandler(Filters.text, artist)]
        },
        fallbacks=[]
    )

    updater.dispatcher.add_handler(conversation_handler)

    test_update = Update(
        update_id=-1,
        message=updater.bot.get_me() if hasattr(updater.bot, 'get_me') else None,
        callback_query=update.callback_query if hasattr(update, 'callback_query') else None,
        inline_query=update.inline_query if hasattr(update, 'inline_query') else None,
        chosen_inline_result=update.chosen_inline_result if hasattr(update, 'chosen_inline_result') else None,
        shipping_query=update.shipping_query if hasattr(update, 'shipping_query') else None,
        pre_checkout_query=update.pre_checkout_query if hasattr(update, 'pre_checkout_query') else None,
        poll=update.poll if hasattr(update, 'poll') else None,
        poll_answer=update.poll_answer if hasattr(update, 'poll_answer') else None,
    )

    updater.dispatcher.process_update(test_update)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
