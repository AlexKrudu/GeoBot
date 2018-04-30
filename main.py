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
    delay = 30 # секунд
    job = job_queue.run_once(change_turn, delay, context=update.message.chat_id, name=start_game)

    # Запоминаем в пользовательских данных созданную задачу.
    chat_data['job'] = job

    # Присылаем сообщение о том, что все получилось.
    update.message.reply_text('Время пошло!')



def start(bot, update):
    update.message.reply_text("Привет! Я - бот для игры в шляпу!Нажмите команду 'сформировать новый список слов' и давайте начнем!", reply_markup=markup)
    return 1


def start_game(bot, update, user_data):
    words_list = []
    file = open("words.txt")
    for i in file:
        words_list.append(i)
    if update.message.text == "сформировать новый список слов":
        update.message.reply_text("Начнем игру! У вас есть ровно 1 минута чтобы обяснить значение как можно большего количества слов. Введите команду 'поехали' чтобы начать игру'", reply_markup=letsgo_markup)
        user_data["total_score"] = [0, 0]
        user_data["team"] = 1
        user_data["current_words"] = random.sample(words_list, 50)
        user_data["current_index"] = -1
        user_data["current_score"] = 0
        user_data["round_counter"] = 0
        return 2
    else:
        update.message.reply_text("Такой команды не существует!")
        return 1


def start_round(bot, update, user_data, job_queue, chat_data):
    if update.message.text == "поехали":
        update.message.reply_text("Ход команды {}!".format(str(user_data["team"])))
        set_timer(bot, update, job_queue, chat_data)
        user_data["current_index"] += 1
        update.message.reply_text("Текущее слово: {}".format(user_data["current_words"][user_data["current_index"]]),
                                  reply_markup=cont_markup)
        return 2
    if user_data["current_index"] == 50:
        update.message.reply_text(
            "Кончились слова! .Количество очков: {}. Игра окончена! Общий счет: Команда 1: {}, Команда 2: {}. Если хотите поиграть еще - введите команду 'сформировать новый список слов'.".format(
                user_data["current_score"], user_data["total_score"][0], user_data["total_score"][1]),
            reply_markup=markup)
        return 1

    job = chat_data['job']
    if not job.enabled:
        job.enabled = True
        user_data["total_score"][user_data["team"] - 1] += user_data["current_score"]
        if user_data["team"] == 1:
            user_data["team"] += 1
        else:
            user_data["team"] -= 1
            user_data["round_counter"] += 1
        if user_data["round_counter"] == 3:
            update.message.reply_text(
                "Количество очков: {}. Игра окончена! Общий счет: Команда 1: {}, Команда 2: {}. Если хотите поиграть еще - введите команду 'сформировать новый список слов'.".format(
                    user_data["current_score"], user_data["total_score"][0], user_data["total_score"][1]), reply_markup=markup)
            return 1

        update.message.reply_text(
            "Количество очков: {}. Чтобы продолжить игру введите команду 'поехали'".format(
                user_data["current_score"]), reply_markup=letsgo_markup)
        user_data["current_score"] = 0
        return 2

    if update.message.text == "угадано":
        user_data["current_score"] += 1
        user_data["current_index"] += 1
        update.message.reply_text("Текущее слово: {}".format(user_data["current_words"][user_data["current_index"]]),
                                  reply_markup=cont_markup)
        return 2
    if update.message.text == "не угадано":
        user_data["current_index"] += 1
        update.message.reply_text("Текущее слово: {}".format(user_data["current_words"][user_data["current_index"]]),
                                  reply_markup=cont_markup)
        return 2


def change_turn(bot, job):
    bot.send_message(job.context, text='Время вышло!')
    job.enabled = False


def help(bot, update):
    update.message.reply_text("Бот-шляпа")


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
            2: [MessageHandler(Filters.text, start_round, pass_user_data=True, pass_job_queue=True, pass_chat_data=True), CommandHandler("set_timer", set_timer, pass_job_queue=True, pass_chat_data=True)],
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
