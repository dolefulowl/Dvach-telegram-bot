from aiogram.types import KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


#vars for navigate in massive of threads
url = 0
media = 1
caption = 2


left_button = InlineKeyboardButton('<—', callback_data='btn1')
right_button = InlineKeyboardButton('—>', callback_data='btn2')
buttons = InlineKeyboardMarkup(row_width=2).add(left_button, right_button)


no_image = "https://avatanplus.com/files/resources/mid/56b0fa8cc6c9d152a352b60e.png"
show_image = "https://prnt.sc/vtumbn"


start_message = "Добро пожаловать. Снова. \n\nДля того, тобы начать листать треды, нужно выбрать предпочитаемую доску, используя команду /Choose."
choose_message = "Доступные на данный момент доски:\n/b\n/fag"
show_message = "Чтобы повторно вызвать интерактивное окно, используйте команду /show."
wrong_board_message = "Пожалуйста, выберите доску, используя список выше."
help_message = "/show - повторно вызывает интерактивное окно.\n/choose - позволяет изменить текущую доску."

available_boards = ['/fag', '/b']
delay = 6000