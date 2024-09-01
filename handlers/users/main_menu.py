from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.default.default_keyboards import admins_panel, main_menu_uzb, main_menu_rus
from loader import dp, types
from utils.db_api.database_settings import is_admin, get_user, get_menu

@dp.callback_query_handler(state='*', text='basket')
async def basket_uz_handler(message: types.Message, state: FSMContext):
    user_basket = await get_user_basket(chat_id=message.chat.id)
    user = await get_user(message.chat.id)
    userga = ""
    if user_basket:
        user_basket_bttn = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        if user['lang'] == 'uz':
            user_basket_bttn.insert(KeyboardButton(text=f"🏘 Asosiy menyu"))
            user_basket_bttn.insert(KeyboardButton(text="🛍 Buyurtma berish"))
            answer = f'😊🛒 Sizning savatingiz'
            userga = f"😊🛒 Savatingiz.\n\n"
        else:
            user_basket_bttn.insert(KeyboardButton(text=f"🏘 Главное меню"))
            user_basket_bttn.insert(KeyboardButton(text="🛍 Разместить заказ"))
            answer = f'😊🛒 Корзина'
            userga = f"😊🛒 Ваша Корзина.\n\n"
        total = 0
        basket_bttn = InlineKeyboardMarkup()
        counter = 0
        for basket in user_basket:
            counter += 1
            basket_bttn.insert(InlineKeyboardButton(text=f'➖', callback_data=f'update_quantity_{basket["id"]}_minus_{user["lang"]}'))
            basket_bttn.insert(InlineKeyboardButton(text=f"{counter}", callback_data='product'))
            basket_bttn.insert(InlineKeyboardButton(text=f'➕', callback_data=f'update_quantity_{basket["id"]}_plus_{user["lang"]}'))
            total += basket['narx']
            userga += f"<b>{counter}</b>. <b>{basket['product']}</b> {int(basket['narx']) // int(basket['miqdor'])} * {basket['miqdor']} = {basket['narx']}\n"
            user_basket_bttn.insert(KeyboardButton(text=f"❌ {basket['product']}"))
        if user['lang'] == 'uz':
            userga += f"\n💰 Ja'mi: <b>{total}</b>"
        else:
            userga += f"\n💰 Общий: <b>{total}</b>"
        await message.answer(text=answer, reply_markup=user_basket_bttn)
        await message.answer(text=userga, reply_markup=basket_bttn)
        await state.set_state('in_basket')
    else:
        if user['lang'] == 'uz':
            userga = f"😕 Kechirasiz sizning savatingiz bosh."
        else:
            userga = f"😕 Извините, ваша корзина пуста."
        await message.answer(text=userga, reply_markup=main_menu_uzb)
        await state.finish()

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
