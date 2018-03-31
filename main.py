from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup
import requests
import random
import sys
import math


def lonlat_distance(a, b):
    degree_to_meters_factor = 111 * 1000
    a_lon, a_lat = a
    b_lon, b_lat = b

    radians_lattitude = math.radians((a_lat + b_lat) / 2.)
    lat_lon_factor = math.cos(radians_lattitude)

    dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
    dy = abs(a_lat - b_lat) * degree_to_meters_factor

    distance = math.sqrt(dx * dx + dy * dy)

    return distance//1000


# Функция определения масштаба карты
def get_bounds(toponym):
    bounds = toponym["boundedBy"]["Envelope"]["lowerCorner"].split(), toponym["boundedBy"]["Envelope"][
        "upperCorner"].split()
    koef = 3 # Подобран опытным путем
    delta = str((float(bounds[1][0]) - float(bounds[0][0])) / koef)
    delta1 = str((float(bounds[1][1]) - float(bounds[0][1])) / koef)
    return delta, delta1


starting_keyboard = [["/start"]]
start_mkup = ReplyKeyboardMarkup(starting_keyboard, one_time_keyboard=True)

reply_keyboard = [['/start_game']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


cont_keyboard = [["/continue"], ["/stop"]]
cont_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)



def start(bot, update, user_data):
    user_data["current_level"] = 0
    update.message.reply_text("Привет! Я - бот GeoGuesser, я вам показываю панораму, а вы должны угадать, в каком месте (на карте) была снята эта панорама. Если вы готовы - нажмите кнопку '/start_game'.", reply_markup=markup)
    return 1


arrows = [["↑"], ["←", "↓", "→"], ["/answer"]]
arrow_markup = ReplyKeyboardMarkup(arrows, one_time_keyboard=False)


marker = [["↑"], ["←", "↓", "→"], ["/Increase_Scale","/Confirm", "/Decrease_Scale"]]
markupper =  ReplyKeyboardMarkup(marker, one_time_keyboard=False)


def start_game(bot, update, user_data):
    user_data["current_level"] += 1
    if user_data["current_level"] == 1:
        user_data["current_score"] = 0
    update.message.reply_text("Начнем уровень {}!".format(user_data["current_level"]))
    while True:
        latt = random.uniform(-122.807306,-67.022079)
        lon = random.uniform(31.892418, 48.991140)
        google_server = "https://maps.googleapis.com/maps/api/streetview?"
        google_data = "https://maps.googleapis.com/maps/api/streetview/metadata?"
        user_data["current_params"] = {
            "location" : ",".join([str(lon), str(latt)]),
            "key" : "AIzaSyAFrWov6xiIgUQwx9YAiPXcNV2qw7BFuZ0",
            "size" : "640x640",
            "heading" : "0"
        }
        response = requests.get(google_data, params=user_data["current_params"])
        json_res = response.json()
        if json_res["status"] != "ZERO_RESULTS":
            user_data["result"] = [latt, lon]
            request = requests.get(google_server, params=user_data["current_params"])
            map_file = "photos/map.png"
            try:
                with open(map_file, "wb") as file:
                    file.write(request.content)
            except IOError as ex:
                print("Ошибка записи временного файла:", ex)
                sys.exit(2)
            bot.sendPhoto(
                update.message.chat.id,  # Идентификатор чата. Куда посылать картинку.
                # Ссылка на static API по сути является ссылкой на картинку.
                photo=open(map_file, 'rb'),
                caption="Если вы готовы дать ответ, нажмите кнопку /answer"
             )
            update.message.reply_text("Вы также можете осмотреться, используя стрелки на клавиатуре", reply_markup=arrow_markup)
            return 2


def help(bot, update):
    update.message.reply_text("Я - повторюша, дядя Хрюша")


def stop(bot, update):
    update.message.reply_text("Пока, пока!")
    return ConversationHandler.END


def handle_direction(bot, update, user_data):
    google_server = "https://maps.googleapis.com/maps/api/streetview?"
    direction = update.message.text
    if direction == "←":
        if user_data["current_params"]["heading"] == "360":
            user_data["current_params"]["heading"] = "0"
        user_data["current_params"]["heading"] = str(int(user_data["current_params"]["heading"]) - 30)
    elif direction == "→":
        if user_data["current_params"]["heading"] == "0":
            user_data["current_params"]["heading"] = "360"
        user_data["current_params"]["heading"] = str(int(user_data["current_params"]["heading"]) + 30)

    request = requests.get(google_server, params=user_data["current_params"])
    map_file = "photos/map.png"
    try:
        with open(map_file, "wb") as file:
            file.write(request.content)
    except IOError as ex:
        print("Ошибка записи временного файла:", ex)
        sys.exit(2)
    bot.sendPhoto(
        update.message.chat.id,  # Идентификатор чата. Куда посылать картинку.
        # Ссылка на static API по сути является ссылкой на картинку.
        photo=open(map_file, 'rb'),
        caption="Если вы готовы дать ответ, нажмите кнопку /answer")


def Increase_Scale(bot, update, user_data):
    static_maps = "http://static-maps.yandex.ru/1.x/"
    if user_data["req_params"]["z"] == "17":
        update.message.reply_text("Максимальный масштаб")
    user_data["koef"] = str(int(user_data["req_params"]["z"]) * float(user_data["koef"]))
    user_data["req_params"]["z"] = str(int(user_data["req_params"]["z"]) + 1)
    user_data["koef"] = str(float(user_data["koef"]) / int(user_data["req_params"]["z"]))
    request = requests.get(static_maps, params=user_data["req_params"])
    map_file = "photos/yamap.png"
    try:
        with open(map_file, "wb") as file:
            file.write(request.content)
    except IOError as ex:
        print("Ошибка записи временного файла:", ex)
        sys.exit(2)
    bot.sendPhoto(
        update.message.chat.id,  # Идентификатор чата. Куда посылать картинку.
        # Ссылка на static API по сути является ссылкой на картинку.
        photo=open(map_file, 'rb'),
        caption="Если вы готовы подтвердить ответ, нажмите кнопку 'Подтвердить'.")


def Decrease_Scale(bot, update, user_data):
    static_maps = "http://static-maps.yandex.ru/1.x/"
    if user_data["req_params"]["z"] == "1":
        update.message.reply_text("Минимальный масштаб")
    user_data["koef"] = str(int(user_data["req_params"]["z"]) * float(user_data["koef"]))
    user_data["req_params"]["z"] = str(int(user_data["req_params"]["z"]) - 1)
    user_data["koef"] = str(float(user_data["koef"]) / int(user_data["req_params"]["z"]))
    request = requests.get(static_maps, params=user_data["req_params"])
    map_file = "photos/yamap.png"
    try:
        with open(map_file, "wb") as file:
            file.write(request.content)
    except IOError as ex:
        print("Ошибка записи временного файла:", ex)
        sys.exit(2)
    bot.sendPhoto(
        update.message.chat.id,  # Идентификатор чата. Куда посылать картинку.
        # Ссылка на static API по сути является ссылкой на картинку.
        photo=open(map_file, 'rb'),
        caption="Если вы готовы подтвердить ответ, нажмите кнопку 'Подтвердить'.")


def Confirm(bot, update, user_data):
    static_maps = "http://static-maps.yandex.ru/1.x/"
    adding = "~" + ",".join([str(i) for i in user_data["result"]]) + ",pm2rdl"
    a = [float(i) for i in user_data["req_params"]["ll"].split(",")]
    mistake = lonlat_distance(a, user_data["result"])
    user_data["req_params"]["pt"] += adding
    del(user_data["req_params"]["z"])
    user_data["req_params"]["pl"] = user_data["req_params"]["ll"] + "," + ",".join([str(i) for i in user_data["result"]])
    request = requests.get(static_maps, params=user_data["req_params"])
    map_file = "photos/yamap.png"
    try:
        with open(map_file, "wb") as file:
            file.write(request.content)
    except IOError as ex:
        print("Ошибка записи временного файла:", ex)
        sys.exit(2)
    bot.sendPhoto(
        update.message.chat.id,  # Идентификатор чата. Куда посылать картинку.
        # Ссылка на static API по сути является ссылкой на картинку.
        photo=open(map_file, 'rb'),
        caption="Вы ошиблись на {} километров".format(mistake))

    score = round(1 - (mistake / 20000), 2) * 100 # 20000 - это максимальная величина, на которую можно ошибиться
    user_data["current_score"] += score
    if user_data["current_level"] == 5:
        update.message.reply_text("Неплохо поиграли! Вы набрали всего {} очков. Если хотите сыграть еще раз, нажмите /start.".format(int(user_data["current_score"])), reply_markup=start_mkup)
        return ConversationHandler.END
    update.message.reply_text("Давайте продолжим!",reply_markup=markup)
    return 1



def handle_marker_direction(bot, update, user_data):
    static_maps = "http://static-maps.yandex.ru/1.x/"
    direction = update.message.text
    if direction == "←":
        cur_value = user_data["req_params"]["pt"].split(",")
        cur_value[0] = str(float(cur_value[0]) - float(user_data["koef"]))
        user_data["req_params"]["pt"] = ",".join(cur_value)
        current_value = user_data["req_params"]["ll"].split(",")
        current_value[0] = str(float(current_value[0]) - float(user_data["koef"]))
        user_data["req_params"]["ll"] = ",".join(current_value)

    if direction == "→":
        cur_value = user_data["req_params"]["pt"].split(",")
        cur_value[0] = str(float(cur_value[0]) + float(user_data["koef"]))
        user_data["req_params"]["pt"] = ",".join(cur_value)
        current_value = user_data["req_params"]["ll"].split(",")
        current_value[0] = str(float(current_value[0]) + float(user_data["koef"]))
        user_data["req_params"]["ll"] = ",".join(current_value)

    if direction == "↑":
        cur_value = user_data["req_params"]["pt"].split(",")
        cur_value[1] = str(float(cur_value[1]) + float(user_data["koef"]))
        user_data["req_params"]["pt"] = ",".join(cur_value)
        current_value = user_data["req_params"]["ll"].split(",")
        current_value[1] = str(float(current_value[1]) + float(user_data["koef"]))
        user_data["req_params"]["ll"] = ",".join(current_value)

    if direction == "↓":
        cur_value = user_data["req_params"]["pt"].split(",")
        cur_value[1] = str(float(cur_value[1]) - float(user_data["koef"]))
        user_data["req_params"]["pt"] = ",".join(cur_value)
        current_value = user_data["req_params"]["ll"].split(",")
        current_value[1] = str(float(current_value[1]) - float(user_data["koef"]))
        user_data["req_params"]["ll"] = ",".join(current_value)

    request = requests.get(static_maps, params=user_data["req_params"])
    map_file = "photos/yamap.png"
    try:
        with open(map_file, "wb") as file:
            file.write(request.content)
    except IOError as ex:
        print("Ошибка записи временного файла:", ex)
        sys.exit(2)
    bot.sendPhoto(
        update.message.chat.id,  # Идентификатор чата. Куда посылать картинку.
        # Ссылка на static API по сути является ссылкой на картинку.
        photo=open(map_file, 'rb'),
        caption="Если вы готовы подтвердить ответ, нажмите кнопку 'Подтвердить'.")


def answer(bot, update, user_data):
    # toponym_to_find = self.address
    static_maps = "http://static-maps.yandex.ru/1.x/"
    user_data["req_params"] = {
        "ll" : "37.620070,55.753630",
        "pt" : "37.620070,55.753630,pm2bll",
        "z" : "2",
        "l": "map"
    }
    try:
        response = requests.get(static_maps, params=user_data["req_params"])
        if response:
            map_file = "yamap.png"
            try:
                with open(map_file, "wb") as file:
                    file.write(response.content)
            except:
                print("Ошибка записи временного файла:")
                sys.exit(2)
    except:
        print("Something is wrong!")

    bot.sendPhoto(
        update.message.chat.id,  # Идентификатор чата. Куда посылать картинку.
        # Ссылка на static API по сути является ссылкой на картинку.
        photo=open(map_file, 'rb'))

    update.message.reply_text("Перемещайте маркер, используя стрелки на клавиатуре", reply_markup=markupper)
    user_data["koef"] = 15
    return 3



def main():
    updater = Updater("552209814:AAE-bRvef3IlttwEHSMkxqk-8HZLDuC1d3k")
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start, pass_user_data=True)],
        states={
            1: [CommandHandler("start_game", start_game, pass_user_data=True)],
            2: [MessageHandler(Filters.text, handle_direction, pass_user_data=True), CommandHandler("answer", answer, pass_user_data=True)],
            3: [MessageHandler(Filters.text, handle_marker_direction, pass_user_data=True), CommandHandler("Increase_Scale", Increase_Scale, pass_user_data=True), CommandHandler("Decrease_Scale", Decrease_Scale, pass_user_data=True), CommandHandler("Confirm", Confirm, pass_user_data=True)]
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