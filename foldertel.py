import os
import telegram

BASE_PATH = '/home/jay/Everything/Music'

def create_album_folder(album_name, artist_name):
    folder_path = os.path.join(BASE_PATH, artist_name, album_name)
    os.makedirs(folder_path, exist_ok=True)
    print(f"Folder '{folder_path}' created!")

def send_message(bot_token, user_id, message):
    bot = telegram.Bot(token=bot_token)
    bot.send_message(chat_id=user_id, text=message)

def get_config():
    config_path = 'config.txt'
    with open(config_path, 'r') as config_file:
        lines = config_file.readlines()
        token = lines[0].strip()
        user_id = lines[1].strip()

    return token, user_id

def main():
    album_name = input("Enter the album name: ")
    artist_name = input("Enter the artist name: ")

    token, user_id = get_config()

    message = "Please provide the AlbumName and Artist Name."
    send_message(token, user_id, message)

    create_album_folder(album_name, artist_name)

if __name__ == '__main__':
    main()
