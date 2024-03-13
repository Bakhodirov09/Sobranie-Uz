from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

lang_select = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🇺🇿 Uzbek Tili", callback_data="uz")
        ],
        [
            InlineKeyboardButton(text="🇷🇺 Русский Язык", callback_data="ru")
        ]
    ]
)

async def plus_minus_def(now, price):
    plus_minus = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=f'➖', callback_data='minus'),
                InlineKeyboardButton(text=f'{now} | {price}', callback_data='now_price'),
                InlineKeyboardButton(text=f'➕', callback_data='plus'),
            ],
            [
                InlineKeyboardButton(text='⬅️ Menyuga qaytish', callback_data='back_main_menu')
            ]
        ]
    )
    return plus_minus

async def plus_minus_def_ru(now: int, price: int):
    plus_minus = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=f'➖', callback_data='minus'),
                InlineKeyboardButton(text=f'{now} | {price}', callback_data='now_price'),
                InlineKeyboardButton(text=f'➕', callback_data='plus'),
            ],
            [
                InlineKeyboardButton(text='⬅️ Вернуться в меню', callback_data='back_main_menu_ru')
            ]
        ]
    )
    return plus_minus

yes_no = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='✅ Xa', callback_data='yes'),
            InlineKeyboardButton(text='❌ Yoq', callback_data='no')
        ]
    ]
)

paymented_rus = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text=f"✅ Я отправил деньги на карту", callback_data='payed')
        ]
    ]
)

paymented = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text=f"✅ Kartaga pul tashladim", callback_data='payed')
        ]
    ]
)
