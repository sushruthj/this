import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

# Create your bot's token
TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'

# Define a function to handle the /start command
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Hello! I'm your Telegram bot.")

# Define a function to handle user messages
def echo(update, context):
    user_id = update.message.from_user['id']
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f"Your user ID is: {user_id}")

def main():
    # Create the Updater and pass your bot's token
    updater = Updater(token=TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register the start command handler
    dispatcher.add_handler(CommandHandler("start", start))

    # Register the message handler
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the bot
    updater.start_polling()

    # Run the bot until Ctrl-C is pressed
    updater.idle()

if __name__ == '__main__':
    main()
