import os
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters

ALBUM, ARTIST = range(2)

def start(update, context):
    update.message.reply_text("Hi! Welcome to the album creator bot. Please enter the album name.")
    return ALBUM

def album(update, context):
    context.user_data['album'] = update.message.text
    update.message.reply_text("Great! Now enter the artist name.")
    return ARTIST

def artist(update, context):
    artist_name = update.message.text
    album_name = context.user_data['album']
    folder_path = f"{artist_name}/{album_name}"
    
    try:
        os.makedirs(folder_path)
        update.message.reply_text(f"Folder created successfully: {folder_path}")
    except OSError as e:
        update.message.reply_text(f"Folder creation failed: {str(e)}")

    return ConversationHandler.END

def cancel(update, context):
    update.message.reply_text("Operation canceled.")
    return ConversationHandler.END

def main():
    updater = Updater("YOUR_BOT_TOKEN", use_context=True)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ALBUM: [MessageHandler(Filters.text, album)],
            ARTIST: [MessageHandler(Filters.text, artist)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    updater.dispatcher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
