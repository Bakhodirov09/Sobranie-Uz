from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.default.default_keyboards import admins_panel, main_menu_uzb, main_menu_rus
from loader import dp, types
from utils.db_api.database_settings import is_admin, get_user, get_menu


@dp.message_handler(state='*', text='🏘 Asosiy menyu')
async def back_main_menu_handler(message: types.Message, state: FSMContext):
    if await is_admin(chat_id=message.chat.id):
        await message.answer(text=message.text, reply_markup=admins_panel)
    else:
        await message.delete()
        await message.answer(text=message.text, reply_markup=main_menu_uzb)
    await state.finish()

@dp.message_handler(state='*', text='🏘 Главное меню')
async def back_main_menu_handler(message: types.Message, state: FSMContext):
    if await is_admin(chat_id=message.chat.id):
        await message.answer(text=message.text, reply_markup=admins_panel)
    else:
        await message.delete()
        lang = await get_user(chat_id=message.chat.id)
        if lang[3] == "uz":
            await message.answer(text=message.text, reply_markup=main_menu_uzb)
        else:
            await message.answer(text=message.text, reply_markup=main_menu_rus)

    await state.finish()

@dp.message_handler(state='*', text='🏘 Наше меню')
async def back_main_menu_handler(message: types.Message, state: FSMContext):
    await message.delete()
    await message.answer(text=message.text, reply_markup=main_menu_rus)
    await state.finish()

@dp.callback_query_handler(state='*', text='main_menu')
async def back_main_menu_handler(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    if await is_admin(chat_id=call.message.chat.id):
        await call.message.answer(text=f"Asosiy menyu", reply_markup=admins_panel)
    else:
        lang = await get_user(chat_id=call.message.chat.id)
        if lang[3] == "uz":
            await call.message.answer(text=f"Asosiy menyu", reply_markup=main_menu_uzb)
        else:
            await call.message.answer(text=f"Главное меню", reply_markup=main_menu_rus)
    await state.finish()

@dp.callback_query_handler(state='*', text='back_main_menu')
async def back_main_menu_handler(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer(text=f"Asosiy menyu", reply_markup=main_menu_uzb)
    await state.finish()

@dp.callback_query_handler(state='*', text='back_main_menu_ru')
async def back_main_menu_handler(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer(text="🏘 Главное меню", reply_markup=main_menu_rus)
    await state.finish()

@dp.callback_query_handler(state='*' ,text='back_menu')
async def back_menu_ru_handler(call: types.CallbackQuery, state: FSMContext):
    menu = await get_menu()
    menu_bttn = InlineKeyboardMarkup(row_width=1)
    for item in menu:
        menu_bttn.insert(InlineKeyboardButton(text=item['menu_name'], callback_data=item['menu_name']))
    menu_bttn.insert(InlineKeyboardButton(text='🏘 Asosiy menyu', callback_data='main_menu'))
    await state.finish()

@dp.callback_query_handler(state='*' ,text='back_menu_ru')
async def back_menu_ru_handler(call: types.CallbackQuery, state: FSMContext):
    menu = await get_menu()
    menu_bttn = InlineKeyboardMarkup(row_width=1)
    for item in menu:
        menu_bttn.insert(InlineKeyboardButton(text=item['menu_name'], callback_data=item['menu_name']))
    menu_bttn.insert(InlineKeyboardButton(text='🏘 Главное меню', callback_data='main_menu'))
    await state.finish()

@dp.callback_query_handler(state='*', text='cancel_uz')
async def back_main_menu_handler(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer(text=f"Asosiy menyu", reply_markup=main_menu_uzb)
    await state.finish()

@dp.callback_query_handler(state='*', text='cancel_ru')
async def back_main_menu_handler(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer(text=f"Asosiy menyu", reply_markup=main_menu_uzb)
    await state.finish()

@dp.message_handler(state='*', text='❌ Bekor Qilish')
async def back_main_menu_handler(message: types.Message, state: FSMContext):
    if await is_admin(chat_id=message.chat.id):
        await message.answer(text=f'❌ Bekor qilindi!', reply_markup=admins_panel)
    else:
        await message.answer(text=f"❌ Bekor qilindi!", reply_markup=main_menu_uzb)
    await state.finish()

@dp.message_handler(state='*', text='❌ Отмена')
async def back_main_menu_handler(message: types.Message, state: FSMContext):
    await message.answer(text=message.text, reply_markup=main_menu_rus)
    await state.finish()
