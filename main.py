import vars
import logging
import asyncio
import json
import os

from urllib.request import urlopen
from minor_functions import caption_preparation, media_preparation
from create_db import db, sql

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import CantParseEntities

bot = Bot(token=os.getenv("TOKEN"))
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)


# Class for using State Machine
class ChooseBoard(StatesGroup):
    waiting_for_choose = State()


def repeat(coro, loop):
    asyncio.ensure_future(coro(), loop=loop)
    loop.call_later(vars.delay, repeat, coro, loop)


@dp.message_handler(commands=['Start'])
async def send_welcome(message: types.Message):
    id = message.chat.id
    sql.execute(f'SELECT id FROM users WHERE id = {id}')
    if sql.fetchone() is None:
        sql.execute(f"INSERT INTO users (id) VALUES (?)", (id,))
        db.commit()
    await bot.send_message(id, vars.start_message)


@dp.message_handler(commands="choose", state="*")
async def choose_your_board(message: types.Message):
    await bot.send_message(message.chat.id, vars.choose_message)
    await ChooseBoard.waiting_for_choose.set()


@dp.message_handler(state=ChooseBoard.waiting_for_choose, content_types=types.ContentTypes.TEXT)
async def commit(message: types.Message, state: FSMContext):
    if message.text.lower() not in vars.available_boards:
        await message.reply(vars.wrong_board_message)
        return
    sql.execute(f"UPDATE users SET ChosenBoard = ? WHERE id = ?", (message.text.lower(), message.chat.id))
    db.commit()
    await bot.send_message(message.chat.id,
                           f"Готово! Ваша текущая доска: {message.text.lower()}.\n" + vars.show_message)

    await state.finish()
    await bot.send_photo(message.chat.id,
                         photo=vars.show_image,
                         caption='Начнем?',
                         reply_markup=vars.buttons)


async def edit_message(chat_id, message_id, current_thread):
    current_board = sql.execute(f'SELECT ChosenBoard FROM users WHERE id = "{chat_id}"').fetchone()[0]
    threads = sql.execute(
        f"SELECT thread_url, photo_url, message FROM boards WHERE board = '{current_board}'").fetchall()

    if current_thread > len(threads) - 1:
        current_thread = 0
    elif current_thread < 0:
        current_thread = len(threads) - 1

    sql.execute(f"UPDATE users SET current_thread = {current_thread} WHERE id = {chat_id}")
    db.commit()

    url = threads[current_thread][vars.url]
    media = threads[current_thread][vars.media]
    caption = threads[current_thread][vars.caption]

    media_object = media_preparation(media, caption)

    url_button = InlineKeyboardButton(text='В тред', url=url)
    buttons = InlineKeyboardMarkup(row_width=2).add(vars.left_button, vars.right_button, url_button)

    try:
        await bot.edit_message_media(media=media_object,
                                     message_id=message_id,
                                     chat_id=chat_id,
                                     reply_markup=buttons)
    except CantParseEntities:
        caption = caption[:caption.rfind("<")]
        media_object = media_preparation(media, caption)
        await bot.edit_message_media(media=media_object,
                                     message_id=message_id,
                                     chat_id=chat_id,
                                     reply_markup=buttons)
    except:
        media = vars.no_image
        media_object = media_preparation(media, caption)
        await bot.edit_message_media(media=media_object,
                                     message_id=message_id,
                                     chat_id=chat_id,
                                     reply_markup=buttons)


@dp.callback_query_handler(lambda c: c.data)
async def process_callback_kb1btn1(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)

    message_id = callback_query.message.message_id
    chat_id = callback_query.message.chat.id
    current_thread = sql.execute(f"SELECT current_thread FROM users WHERE id = {chat_id}").fetchone()[0]

    code = int(callback_query.data[-1])
    if code == 1:
        current_thread = current_thread + 1
    elif code == 2:
        current_thread = current_thread - 1
    await edit_message(chat_id, message_id, current_thread)


@dp.message_handler(commands=['help'])
async def send_welcome(message: types.Message):
    await bot.send_message(message.chat.id, vars.help_message)


async def update():
    # -------------------------------------DELETE OLD ONE
    sql.execute('''DROP TABLE boards''')
    db.commit()
    # -------------------------------------CREAT NEW ONE
    sql.execute("""CREATE TABLE boards (
      board TEXT,
      thread_url TEXT,
      photo_url TEXT,
      message TEXT)""")
    db.commit()
    # --------------------------------------
    for board in vars.available_boards:
        url = f'https://2ch.hk/{board}/catalog_num.json'
        body = urlopen(url).read()
        data = json.loads(body)
        for thread in data["threads"]:
            media = "https://2ch.hk" + thread["files"][0]['path']
            num_url = f'''https://2ch.hk/{board}/res/{thread["num"]}.html'''
            comment = caption_preparation(thread["comment"])
            sql.execute(f"INSERT INTO boards VALUES (?,?,?,?)", (board, num_url, media, comment), )
            db.commit()


@dp.message_handler(commands=['show'])
async def send_welcome1(message: types.Message):
    await bot.send_photo(message.chat.id,
                         photo=vars.show_image,
                         caption='Начнем?',
                         reply_markup=vars.buttons)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.call_later(vars.delay, repeat, update, loop)
    executor.start_polling(dp, skip_updates=True, loop=loop)
