import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, filters
from telegram import Bot, Update
from telegram.ext import JobQueue

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

def get_bot_token():
    with open('config.txt', 'r') as f:
        return f.read().strip()

# Define a function to handle the /start command
def start(update: Update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hello! I'm your Telegram bot.")

# Define a function to handle user messages
def echo(update: Update, context):
    user_id = update.message.from_user['id']
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Your user ID is: {user_id}")

def main():
    # Get the bot token from token.txt
    TOKEN = get_bot_token()

    # Create the Bot instance
    bot = Bot(token=TOKEN)

    # Create the Updater with the Bot instance and JobQueue
    updater = Updater(bot=bot, job_queue=JobQueue())

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register the start command handler
    dispatcher.add_handler(CommandHandler("start", start))

    # Register the message handler
    dispatcher.add_handler(MessageHandler(filters.text & ~filters.command, echo))

    # Start the bot
    updater.start_polling()

    # Run the bot until Ctrl-C is pressed
    updater.idle()

if __name__ == '__main__':
    main()
