from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, ConversationHandler
from telegram import ReplyKeyboardRemove
import requests
import random
import sys
import math
import os
from images import *
from keyboards import *
from urllib3.contrib.socks import SOCKSProxyManager


def set_timer(bot, update, job_queue, chat_data):
    # создаем задачу task в очереди job_queue через 20 секунд
    # передаем ей идентификатор текущего чата (будет доступен через job.context)
    delay = 5 # секунд
    job = job_queue.run_once(change_turn, delay, context=update.message.chat_id, name=start_game)

    # Запоминаем в пользовательских данных созданную задачу.
    chat_data['job'] = job

    # Присылаем сообщение о том, что все получилось.
    update.message.reply_text('Вернусь через 20 секунд!')



def start(bot, update):
    update.message.reply_text("Привет! Я - бот для игры в шляпу!Нажмите команду 'сформировать новый список слов' и давайте начнем!", reply_markup=markup)
    return 1


def start_game(bot, update, user_data):
    words_list = []
    file = open("words.txt")
    for i in file:
        words_list.append(i)
    if update.message.text == "сформировать новый список слов":
        update.message.reply_text("Начнем игру! У вас есть ровно 1 минута чтобы обяснить значение как можно большего количества слов. Введите команду '/set_timer чтобьы начать игру'")
        user_data["current_words"] = random.sample(words_list, 50)
        user_data["current_index"] = -1
        user_data["current_score"] = 0
        return 2
    else:
        update.message.reply_text("Такой команды не существует!")
        return 1


def start_round(bot, update, user_data):
    if update.message.text == "угадано":
        user_data["current_score"] += 1
    user_data["current_index"] += 1
    update.message.reply_text("Текущее слово: {}".format(user_data["current_words"].pop(user_data["current_index"])), reply_markup=cont_markup)
    return 2


def change_turn(bot, job):
    bot.send_message(job.context, text='Вернулся!')


def help(bot, update):
    update.message.reply_text("This bot was created by Alexandr Krudu. This bot uses Google Street View Image API"
                              " ('https://developers.google.com/maps/documentation/streetview/intro?hl=ru',"
                              " Telegram API ('https://core.telegram.org/api'),"
                              " Yandex Static Maps API ('https://tech.yandex.ru/maps/staticapi/'). Check project repository"
                              " 'https://github.com/AlexKrudu/GeoBot'."
                              " Also check original project: 'https://geoguessr.com'! Thank you for using this bot!")


def stop(bot, update):
    update.message.reply_text("Пока, пока!", reply_markup=ReplyKeyboardRemove())
    os.remove(map_image)
    os.remove(panoram_image)
    return ConversationHandler.END


def main():
    updater = Updater("552209814:AAE-bRvef3IlttwEHSMkxqk-8HZLDuC1d3k")
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            1: [MessageHandler(Filters.text, start_game, pass_user_data=True)],
            2: [MessageHandler(Filters.text, start_round, pass_user_data=True), CommandHandler("set_timer", set_timer, pass_job_queue=True, pass_chat_data=True)],
        },
        fallbacks=[CommandHandler("stop", stop)]
    )

    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler("help", help))
    print("Bot started")
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
