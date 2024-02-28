import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters, CallbackContext

ALBUM, ARTIST = range(2)

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hi! Welcome to the album creator bot. Please enter the album name.")
    return ALBUM

def album(update: Update, context: CallbackContext):
    context.user_data['album'] = update.message.text
    update.message.reply_text("Great! Now enter the artist name.")
    return ARTIST

def artist(update: Update, context: CallbackContext):
    artist_name = update.message.text
    album_name = context.user_data['album']
    folder_path = f"{artist_name}/{album_name}"
    
    try:
        os.makedirs(folder_path)
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Folder created successfully: {folder_path}")
    except OSError as e:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Folder creation failed: {str(e)}")

    return ConversationHandler.END

def main():
    updater = Updater("YOUR_BOT_TOKEN")

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(ConversationHandler(
        entry_points=[MessageHandler(Filters.private & ~Filters.command, start)],
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
