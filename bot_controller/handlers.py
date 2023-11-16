import os

import numpy as np
import telebot
from matplotlib import image as img
from PIL import Image

import output
from db import db_app
from model.palette_extractor import PaletteExtractor
from model.image_transformer import ImageTransformer


class Bot:

    def __init__(self):
        self.photo_event_type = "EXTRACT"
        self.saved_colors = [[29, 24, 20], [203, 191, 189], [121, 92, 75], [235, 190, 13], [106, 46, 16]]

    def bot_runner(self):
        token = os.getenv('TOKEN')
        bot = telebot.TeleBot(token)

        @bot.message_handler(commands=["start"])
        def start(message, res=False):
            bot.send_message(message.chat.id, 'Добро пожаловать! Для получения палитры из основных '
                                              'цветов изображения, отправьте мне фото 📸\n'
                                              'Для получения полного списка команд введите /help')

        @bot.message_handler(commands=["help"])
        def handle_help(message):
            bot.send_message(message.chat.id,
                             "Доступные команды:\n"
                             "/extractColors - получить палитру с основными цветами изображения\n"
                             "/transformImage - редактировать изображение\n"
                             "/changeColorsNumber <number> - изменить количество цветов в палитре (по умолчанию - 5)\n")

        @bot.message_handler(commands=["changeColorsNumber"])
        def handle_help(message):
            args = message.text.split()
            if len(args) != 2:
                bot.send_message(message.chat.id, "Введите одно число после команды через пробел")
            else:
                if args[1].isdigit():
                    connection = db_app.get_connection()
                    try:
                        with connection.cursor() as cursor:
                            cursor.execute("""
                                        INSERT INTO usersInfo (chat_id, clusters) 
                                        VALUES (%s, %s)
                                        ON CONFLICT (chat_id) 
                                        DO UPDATE SET clusters = EXCLUDED.clusters;
                                        """, (str(message.chat.id), args[1]))
                            connection.commit()
                            bot.send_message(message.chat.id, "Количество цветов успешно обновлено")
                    except Exception as e:
                        print("Произошла ошибка: ", e)
                        bot.send_message(message.chat.id, "Произошла ошибка при обновлении количества цветов")
                    finally:
                        db_app.release_connection(connection)
                else:
                    bot.send_message(message.chat.id, "Введите одно число после команды через пробел")

        @bot.message_handler(commands=["extractColors"])
        def handle_extract_colors(message):
            self.photo_event_type = "EXTRACT"
            bot.send_message(message.chat.id, 'Введите изоборажение')

        @bot.message_handler(commands=["transformImage"])
        def handle_extract_colors(message):
            self.photo_event_type = "TRANSFORM"
            bot.send_message(message.chat.id, 'Введите изоборажение')

        @bot.message_handler(content_types=["text"])
        def handle_text(message):
            bot.send_message(message.chat.id, "Такой команды я не знаю 😟")

        @bot.message_handler(content_types=["photo"])
        def handle_photo(message):
            if self.photo_event_type == "EXTRACT":
                extract_colors(message)
            else:
                transform_image(message)

        def extract_colors(message):
            chat_id = str(message.chat.id)
            connection = db_app.get_connection()
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT clusters FROM usersInfo WHERE chat_id = %s;", (chat_id,))
                    record = cursor.fetchone()

                    if record is not None:
                        val = record[0]  # Получение значения clusters
                    else:
                        val = 5
                    file_info = bot.get_file(message.photo[1].file_id)
                    downloaded_file = bot.download_file(file_info.file_path)
                    file_name = str(message.chat.id) + '.jpg'

                    with open(file_name, 'wb') as new_file:
                        new_file.write(downloaded_file)

                    image = img.imread(file_name)

                    palette_extractor = PaletteExtractor(val)
                    palette_extractor.fit(image)
                    colors = palette_extractor.get_colors()
                    saved_colors = colors
                    print(colors)
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
            except Exception as e:
                print("Произошла ошибка: ", e)
            finally:
                db_app.release_connection(connection)

        def transform_image(message):
            file_info = bot.get_file(message.photo[1].file_id)

            downloaded_file = bot.download_file(file_info.file_path)
            file_name = str(message.chat.id) + '.jpg'

            with open(file_name, 'wb') as new_file:
                new_file.write(downloaded_file)

            image = img.imread(file_name)
            image = ImageTransformer(self.saved_colors).transform(image)

            im = Image.fromarray(np.array(image, dtype=np.uint8))
            im.save("t_" + file_name)

            photo = open("t_" + file_name, 'rb')
            bot.send_photo(message.chat.id, photo)


        bot.polling(none_stop=True, interval=0)
