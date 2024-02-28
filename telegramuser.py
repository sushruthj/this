import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, filters
from telegram import Bot

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

def get_bot_token():
    with open('config.txt', 'r') as f:
        return f.read().strip()

# Define a function to handle the /start command
def start(bot, update):
    update.message.reply_text("Hello! I'm your Telegram bot.")

# Define a function to handle user messages
def echo(bot, update):
    user_id = update.message.from_user['id']
    update.message.reply_text(f"Your user ID is: {user_id}")

def main():
    # Get the bot token from token.txt
    TOKEN = get_bot_token()

    # Create the Bot instance
    bot = Bot(token=TOKEN)

    # Create the Updater with the Bot instance
    updater = Updater(bot=bot)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register the start command handler
    dispatcher.add_handler(CommandHandler("start", start))

    # Register the message handler
    dispatcher.add_handler(MessageHandler(filters.text & (~filters.command), echo))

    # Start the bot
    updater.start_polling()

    # Run the bot until Ctrl-C is pressed
    updater.idle()

if __name__ == '__main__':
    main()
