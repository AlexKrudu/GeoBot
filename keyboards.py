from telegram import ReplyKeyboardMarkup

starting_keyboard = [["/start"]]
start_mkup = ReplyKeyboardMarkup(starting_keyboard, one_time_keyboard=True)

reply_keyboard = [['/start_game'], ['/stop']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


cont_keyboard = [["/continue"], ["/stop"]]
cont_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


arrows = [["↑"], ["←", "↓", "→"], ["/answer"]]
arrow_markup = ReplyKeyboardMarkup(arrows, one_time_keyboard=False)


marker = [["↑"], ["←", "↓", "→"], ["/Increase_Scale","/Confirm", "/Decrease_Scale"]]
markupper =  ReplyKeyboardMarkup(marker, one_time_keyboard=False)