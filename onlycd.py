from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import os

# Your Telegram user ID
YOUR_USER_ID = "YOUR_USER_ID"

# Define a function to handle the /start command
def start(update, context):
    if str(update.message.from_user.id) == YOUR_USER_ID:
        update.message.reply_text("Welcome to the Album Organizer bot! Please send me the name of the artist.")
    else:
        update.message.reply_text("Sorry, you are not authorized to use this bot.")

# Define a function to handle the artist name
def receive_artist(update, context):
    if str(update.message.from_user.id) == YOUR_USER_ID:
        context.user_data['artist'] = update.message.text
        update.message.reply_text("Great! Now, please send me the name of the album.")
    else:
        update.message.reply_text("Sorry, you are not authorized to use this bot.")

# Define a function to handle the album name
def receive_album(update, context):
    if str(update.message.from_user.id) == YOUR_USER_ID:
        artist = context.user_data.get('artist')
        album = update.message.text
        folder_path = f"{artist}/{album}"

        # Create the folder structure
        os.makedirs(folder_path, exist_ok=True)
        
        update.message.reply_text(f"Folder '{album}' under '{artist}' has been created.")
    else:
        update.message.reply_text("Sorry, you are not authorized to use this bot.")

# Set up the Telegram bot
def main():
    # Token for the Telegram Bot API
    updater = Updater("YOUR_BOT_TOKEN", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Define handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.regex(r'^[^/].*'), receive_artist))
    dp.add_handler(MessageHandler(Filters.regex(r'^[^/].*'), receive_album))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main()