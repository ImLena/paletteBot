import os

import boto3
import telebot
from matplotlib import image as img
import output
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
        ncs = palette_extractor.get_ncs()
        print(ncs)

        sorted_colors = sorted(colors, key=output.calculate_luminance, reverse=True)
        output.generate_palette(sorted_colors, file_name)

        photo = open(file_name, 'rb')
        bot.send_photo(message.chat.id, photo)
        bot.send_message(message.chat.id, output.generate_color_message("HEX", hexes),
                         parse_mode='MarkdownV2')
        bot.send_message(message.chat.id, output.generate_color_message("RAL", rals),
                         parse_mode='MarkdownV2')
        bot.send_message(message.chat.id, output.generate_color_message("NCS", ncs),
                         parse_mode='MarkdownV2')

    bot.polling(none_stop=True, interval=0)


if __name__ == '__main__':
    bot_runner()
