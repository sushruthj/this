import os
import telegram
import retry

BASE_PATH = '/home/jay/Everything/Music'
CONFIG_PATH = 'config.txt'

def create_album_folder(album_name, artist_name):
    folder_path = os.path.join(BASE_PATH, artist_name, album_name)
    os.makedirs(folder_path, exist_ok=True)
    print(f"Folder '{folder_path}' created!")

def send_message(bot_token, user_id, message):
    bot = telegram.Bot(token=bot_token)
    bot.send_message(chat_id=user_id, text=message)

@retry.retry(tries=3, delay=1, backoff=2)
def get_response(bot_token):
    bot = telegram.Bot(token=bot_token)
    updates = bot.get_updates(timeout=10)
    if updates:
        last_update = updates[-1]
        message_text = last_update.message.text
        return message_text
    else:
        raise Exception("No response received")

def get_config():
    with open(CONFIG_PATH, 'r') as config_file:
        lines = config_file.readlines()
        token = lines[0].strip()
        user_id = lines[1].strip()
    return token, user_id

def main():
    token, user_id = get_config()

    message = "Please provide the AlbumName and Artist Name."
    send_message(token, user_id, message)

    response = ""
    while not response:
        try:
            response = get_response(token)
        except Exception as e:
            print(f"Error: {str(e)}")
            retry_option = input("Retry? (y/n): ")
            if retry_option.lower() == 'n':
                return

    album_name, artist_name = map(str.strip, response.split(','))
    create_album_folder(album_name, artist_name)

if __name__ == '__main__':
    main()
