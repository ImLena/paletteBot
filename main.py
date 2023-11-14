import os

import boto3
import telebot
from matplotlib import image as img
from matplotlib import pyplot as plt

from model.palette_extractor import PaletteExtractor


def bot_runner():
    session = boto3.session.Session()

    token = os.getenv('TOKEN')
    bot = telebot.TeleBot(token)

    @bot.message_handler(commands=["start"])
    def start(message, res=False):
        bot.send_message(message.chat.id, 'Добро пожаловать! Для получения палитры из основных '
                                          'цветов изображения, отправьте мне фото 📸\n'
                                          'Для получения полного списка команд введите /help')

    @bot.message_handler(content_types=["photo"])
    def handle_photo(message):
        file_info = bot.get_file(message.photo[1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        file_name = str(message.chat.id) + '.jpg'
        with open(file_name, 'wb') as new_file:
            new_file.write(downloaded_file)
        new_file.close()
        image = img.imread(file_name)

        palette_extractor = PaletteExtractor(5)
        palette_extractor.fit(image)
        colors = palette_extractor.get_colors()
        hexes = palette_extractor.get_hexes()
        print(hexes)
        rals = palette_extractor.get_rals()
        print(rals)

        plt.switch_backend('Agg')
        plt.imshow([colors])
        plt.savefig(file_name)
        photo = open(file_name, 'rb')
        bot.send_photo(message.chat.id, photo)

    bot.polling(none_stop=True, interval=0)

if __name__ == '__main__':
    bot_runner()
