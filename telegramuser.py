from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Define a function to handle the /start command
def start(update, context):
    update.message.reply_text('Hello! Send any message to get your user ID.')

# Define a function to handle incoming messages
def echo(update, context):
    user_id = update.message.from_user.id
    update.message.reply_text(f'Your user ID is: {user_id}')

def main():
    # Create an Updater object and pass in your bot's token
    updater = Updater("6409123335:AAHm_lvLX0kUGTmpp4kDZZYCG5LIBC7DcVs", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add command handler for the /start command
    dp.add_handler(CommandHandler("start", start))

    # Add message handler for all incoming messages
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main()