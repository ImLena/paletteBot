import os

import telebot
import boto3


def bot_runner():
    session = boto3.session.Session()

    bot = telebot.TeleBot(os.environ['TOKEN'])

    @bot.message_handler(commands=["start"])
    def start(message, res=False):
        bot.send_message(message.chat.id, 'Добро пожаловать! Для получения палитры из основных '
                                          'цветов изображения, отправьте мне фото 📸\n'
                                          'Для получения полного списка команд введите /help')

    bot.polling(none_stop=True, interval=0)


if __name__ == '__main__':
    bot_runner()
