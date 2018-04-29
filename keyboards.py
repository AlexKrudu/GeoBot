from telegram import ReplyKeyboardMarkup

reply_keyboard = [['сформировать новый список слов']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


cont_keyboard = [["угадано"], ["не угадано"]]
cont_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
