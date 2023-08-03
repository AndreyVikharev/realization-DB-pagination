from commands.genres import *
import logging
import asyncio
from config_reader import config
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, Text


load_dotenv()

logging.basicConfig(level=logging.INFO)


bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher()


@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    command_keyboard = [[types.KeyboardButton(text='Просмотреть рейтинг'),
                        types.KeyboardButton(text='Поиск манги по жанрам')
                         ],
                        [types.KeyboardButton(text='Поиск по ключевым словам'),
                        types.KeyboardButton(text='Отображение истории запросов')
                         ],
                        [types.KeyboardButton(text='Избранное')]
                        ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=command_keyboard,
                                         resize_keyboard=True,
                                         input_field_placeholder='Выберите один из пунктов'
                                         )
    await message.answer('Данный бот создан для мониторинга сайта манги Desu.me.',
                         reply_markup=keyboard)


@dp.callback_query(Text(startswith='hide'))
async def hide_keyboard(callback: types.CallbackQuery):
    """Функционал пагинации"""

    await bot.delete_message(message_id=callback.message.message_id, chat_id=callback.message.chat.id)


@dp.message(Text('Поиск манги по жанрам'))
async def genres(message: types.Message):
    buttons = []
    row_list = []
    for item in get_genres():

        row_list.append(types.InlineKeyboardButton(text=item, callback_data=f'genre:{item[:18:]}:1'))

        if (len(row_list) == 3) or (len(item) >= 15):
            buttons.append(row_list)
            row_list = []

    buttons.append(row_list)
    buttons.append([types.InlineKeyboardButton(text='Скрыть', callback_data='hide')
                    ])
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer('Выберите жанр:', reply_markup=keyboard)


@dp.callback_query(Text(startswith='genre:'))
async def send_genres_search(callback: types.CallbackQuery):
    genre = (callback.data).split(':')
    manga_list = get_manga(genre[1])
    buttons = []
    if len(genre) == 3:
        max_page = len(manga_list)
        page = int(genre[2])

        if page == 1:
            buttons = [[types.InlineKeyboardButton(text=f'{manga_list[page - 1]}',
                                                   callback_data=f'name:{(manga_list[page - 1])[:12:]}')],
                       [types.InlineKeyboardButton(text=f'{page}/{max_page}',
                                                   callback_data='Сколько/Из'),
                        types.InlineKeyboardButton(text='Вперёд-->',
                                                   callback_data=(':'.join(genre[0:2])) + f':{page + 1}')],
                       [types.InlineKeyboardButton(text='Скрыть', callback_data='hide')],
                       [types.InlineKeyboardButton(text='Вывести всё списком',
                                                   callback_data=':'.join(genre[0:2]))]
                       ]

        elif page == max_page:
            buttons = [[types.InlineKeyboardButton(text=f'{manga_list[page - 1]}',
                                                   callback_data=f'name:{(manga_list[page - 1])[:12:]}')],
                       [types.InlineKeyboardButton(text='<--Назад',
                                                   callback_data=(':'.join(genre[0:2])) + f':{page - 1}'),
                        types.InlineKeyboardButton(text=f'{page}/{max_page}', callback_data='Сколько/Из')],
                       [types.InlineKeyboardButton(text='Скрыть', callback_data='hide')],
                       [types.InlineKeyboardButton(text='Вывести всё списком',
                                                   callback_data=':'.join(genre[0:2]))]
                       ]

        else:
            buttons = [[types.InlineKeyboardButton(text=f'{manga_list[page - 1]}',
                                                   callback_data=f'name:{(manga_list[page - 1])[:12:]}')],
                       [types.InlineKeyboardButton(text='<--Назад',
                                                   callback_data=(':'.join(genre[0:2])) + f':{page - 1}'),

                       types.InlineKeyboardButton(text=f'{page}/{max_page}',
                                                  callback_data='Сколько/Из'),

                        types.InlineKeyboardButton(text='Вперёд-->',
                                                   callback_data=(':'.join(genre[0:2])) + f':{page + 1}')],
                       [types.InlineKeyboardButton(text='Скрыть', callback_data='hide')],
                       [types.InlineKeyboardButton(text='Вывести всё списком',
                                                   callback_data=':'.join(genre[0:2]))]
                       ]

        keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

        await callback.message.edit_text(f'Манга с жанром {genre[1]}:\n',
                                         reply_markup=keyboard)
        await callback.answer()

    elif len(genre) == 2:

        for item in manga_list:
            buttons.append([types.InlineKeyboardButton(text=item, callback_data=f'name:{item[:12:]}')])
        buttons.append([types.InlineKeyboardButton(text='Вывести книжкой',
                                                   callback_data=(':'.join(genre[0:2])) + ':1')])

        keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

        await callback.message.edit_text(f'Манга с жанром {genre[1]}:\n',
                                         reply_markup=keyboard)
        await callback.answer()


async def main():
    await dp.start_polling(bot)


asyncio.run(main())
