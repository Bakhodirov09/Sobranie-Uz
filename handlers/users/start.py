import random

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.types import ReplyKeyboardRemove

from lang import translate_uz_to_ru
from utils.db_api.database_settings import *
from keyboards.default.default_keyboards import *
from keyboards.inline.inline_keyboards import *
from loader import dp
from states.states import *

@dp.message_handler(CommandStart())
async def start_handler(message: types.Message, state: FSMContext):
    if await is_admin(chat_id=message.chat.id):
        adminga = f"Xush Kelibsiz"
        await message.answer(text=adminga, reply_markup=admins_panel)
    else:
        if await get_user(chat_id=message.chat.id):
            user = await get_user(chat_id=message.from_id)
            if user[3] == "uz":
                userga = f"😊 Xush Kelibsiz"
                await message.answer(text=userga, reply_markup=main_menu_uzb)
            else:
                userga = f"😊 ДОБРО ПОЖАЛОВАТЬ!"
                await message.answer(text=userga.capitalize(), reply_markup=main_menu_rus)
        else:
            userga = f"""
🇺🇿 O'zinigizga Qulay Tilni Tanlang.
🇷🇺 Выберите предпочитаемый язык.
"""
            await message.answer(text=userga, reply_markup=lang_select)
            await Register_States.select_lang.set()

@dp.callback_query_handler(state=Register_States.select_lang)
async def get_language_handler(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await state.update_data({
        "lang": call.data
    })
    if call.data == "uz":
        userga = f"🇺🇿 Uzbek Tili Tanlandi.\n✍️ Iltimos Toliq Isminngizni Kiriting."
        await call.message.answer(text=userga, reply_markup=ReplyKeyboardRemove())
    else:
        userga = f"🇷🇺 Выбран русский язык.\n✍️ Введите свое полное имя"
        await call.message.answer(text=userga, reply_markup=ReplyKeyboardRemove())
    await Register_States.full_name.set()

@dp.message_handler(state=Register_States.full_name)
async def enter_full_name_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data({
        "full_name": message.text,
        "lang": data["lang"]
    })
    if data["lang"] == "uz":
        userga = f"📞 Iltimios: {message.text} Telefon Raqamingizni Tugma Orqali Yuboring."
        await message.answer(text=userga, reply_markup=send_phone_number)
    else:
        userga = f"📞 Пожалуйста: {message.text} Отправьте свой номер телефона через кнопку"
        await message.answer(text=userga, reply_markup=send_phone_number_rus)
    await Register_States.phone_number.set()

@dp.message_handler(state=Register_States.phone_number, content_types=types.ContentType.CONTACT)
async def send_phone_number_handler(message: types.Message, state: FSMContext):
    username = f""
    phone_number = f""
    if message.contact.phone_number[0] != "+":
        phone_number = f"+{message.contact.phone_number}"
    else:
        phone_number = f"{message.contact.phone_number}"

    if message.from_user.username:
        username = f"@{message.from_user.username}"
    else:
        username = "Mavjud Emas"

    await state.update_data({
        "phone_number": phone_number,
        "username": username,
        "chat_id": message.chat.id
    })

    data = await state.get_data()
    if await insert_user(data=data):
        userga = f"🥳 Tabriklaymiz Siz Bizning Bo'tdan Muvaffqqiyatli Ro'yxatdan O'tdingiz!"
        if data["lang"] == "uz":
            await message.answer(text=userga, reply_markup=main_menu_uzb)
        else:
            await message.answer(text=translate_uz_to_ru(text=userga), reply_markup=main_menu_rus)
    else:
        if data["lang"] == "uz":
            userga = f"Kecirasiz botda xatolik mavjud.Iltimos /start buyrugini kiritib qayta urinib koring.\nXatolik haqida ma'lumotni @bakhodirovv_09 ga xabar berishingizni so'raymiz."
            await message.answer(text=userga, reply_markup=ReplyKeyboardMarkup())
        else:
            userga = f"Извините, в боте произошла ошибка. Попробуйте еще раз, набрав /start.\nПожалуйста, сообщите об ошибке @bakhodrovv_09."
            await message.answer(text=userga, reply_markup=ReplyKeyboardRemove())
    await state.finish()

# Uzbek Functions

@dp.message_handler(text="🍴 Menyu")
async def open_menu_handler(message: types.Message, state: FSMContext):

    photo = await get_main_menu_logo()
    lang = await get_user(chat_id=message.chat.id)
    menyu = InlineKeyboardMarkup(row_width=2)
    if lang[3] == "uz":
        userga = f"😋 Bizning Menyu"
        menus = await get_menu()
        for meal in menus:
            menyu.insert(InlineKeyboardButton(text=f"{meal['menu_name']}", callback_data=f"{meal['menu_name']}_uz"))
        menyu.insert(InlineKeyboardButton(text='🏘 Asosiy Menu', callback_data='main_menu'))
        await message.answer(text=userga, reply_markup=main_menu_back_uz)
    else:
        userga = f"😋 Наше меню"
        menus = await get_menu_ru()
        for meal in menus:
            menyu.insert(InlineKeyboardButton(text=f"{meal['menu_name']}", callback_data=f"{meal['menu_name']}_ru"))
        menyu.insert(InlineKeyboardButton(text='🏘 Главное меню', callback_data='main_menu'))
        await message.answer(text=userga, reply_markup=main_menu_back_ru)
    await message.answer_photo(photo=photo['photo'], reply_markup=menyu)
    await state.set_state('menu')

@dp.message_handler(text="🍴 Меню")
async def open_menu_handler(message: types.Message, state: FSMContext):

    photo = await get_main_menu_logo()
    menyu_ru = InlineKeyboardMarkup(row_width=2)
    userga = f"😋 Наше меню"
    menus = await get_menu_ru()
    for meal in menus:
        menyu_ru.insert(InlineKeyboardButton(text=f"{meal['menu_name']}", callback_data=f"{meal['menu_name']}_ru"))
    menyu_ru.insert(InlineKeyboardButton(text='🏘 Главное меню', callback_data='main_menu_ru'))
    await message.answer(text=userga, reply_markup=main_menu_back_ru)
    await message.answer_photo(photo=photo['photo'], reply_markup=menyu_ru)
    await state.set_state('menu')

@dp.callback_query_handler(state='menu')
async def menu_handler(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    data = await state.get_data()
    lang = await get_user(chat_id=call.message.chat.id)
    if await get_fast_foods_in_menu(menu_name=call.data[0:-3]):
        if call.data[-3:] == '_uz':
            await state.update_data({
                'page': 'menu_uz',
                'menu_name': call.data[0:-3]
            })
            menu_pic = await get_menu_pic(menu_name=call.data[0:-3])
            meals = InlineKeyboardMarkup(row_width=2)
            userga = f'😋 {call.data[0:-3]} Menyu'
            for meal in await get_fast_foods_in_menu(menu_name=call.data[0:-3]):
                meals.insert(InlineKeyboardButton(text=f'{meal["food_name"]}', callback_data=f'{meal["food_name"]}'))
            meals.insert(InlineKeyboardButton(text=f'⬅️ Ortga', callback_data='back_uz'))
            await call.message.answer_photo(photo=menu_pic['menu_picture'], caption=userga, reply_markup=meals)
            await state.set_state('menu')
        else:
            await state.update_data({
                'page': 'menu_ru',
                'menu_name': call.data[0:-3]
            })
            menu_pic = await get_menu_pic(menu_name=call.data[0:-3])
            meals = InlineKeyboardMarkup(row_width=2)
            userga = f'😋 {call.data[0:-3]} Меню'
            for meal in await get_fast_foods_in_menu(menu_name=call.data[0:-3]):
                meals.insert(InlineKeyboardButton(text=f'{meal["food_name"]}', callback_data=f'{meal["food_name"]}'))
            meals.insert(InlineKeyboardButton(text=f'⬅️ Назад', callback_data='back_ru'))
            meals.insert(InlineKeyboardButton(text=f'🏘 Главное меню', callback_data='main_menu_ru'))
            await call.message.answer_photo(photo=menu_pic['menu_picture'], caption=userga, reply_markup=meals)
            await state.set_state('menu')
    elif await get_fast_food_in_menu(menu_name=data['menu_name'], fast_food_name=call.data):
        fast_food = await get_fast_food_in_menu(fast_food_name=call.data, menu_name=data['menu_name'])
        photo = fast_food['photo']
        food_name = fast_food['food_name']
        price = fast_food['price']
        await state.update_data({
            "photo": photo,
            "food_name": food_name,
            'menu_name': fast_food['menu'],
            "price": price,
        })
        if lang[3] == "uz":
            userga = f"""
😋 {food_name}:
Mahsulot Haqida: <b>{fast_food['description']}</b>
💰 Narxi: {price}
"""
            await call.message.answer_photo(photo=photo, caption=userga, reply_markup=await plus_minus_def(0, 0))
        else:
            userga = f"""
😋 {food_name}:\t
О продукте: <b>{fast_food['description']}</b>
💰 Цена: {price}
"""
            await call.message.answer_photo(photo=photo, caption=userga, reply_markup=await plus_minus_def_ru(0,0))
        await state.set_state('got_food')

@dp.callback_query_handler(state='got_food', text="plus")
async def plus_handler(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.update_data({
        "food_name": data['food_name'],
        "menu_name": data['menu_name'],
        "price": data['price']
    })
    lang = await get_user(chat_id=call.message.chat.id)
    if await is_in_basket(food_name=data['food_name'], menu_name=data['menu_name'], chat_id=call.message.chat.id):
        miqdor = await get_user_miqdor(chat_id=call.message.chat.id, fast_food=data['food_name'], menu_name=data['menu_name'])
        await update_product_miqdor(miqdor=miqdor[2], product_name=data['food_name'], chat_id=call.message.chat.id, narx=data['price'], menu_name=data['menu_name'])
        new_miq = await get_user_miqdor(chat_id=call.message.chat.id, fast_food=data['food_name'], menu_name=data['menu_name'])
        if lang[3] == "uz":
            await call.answer(text=f"{data['food_name']} Miqdori 1 taga oshirildi.")
            await call.message.edit_reply_markup(reply_markup=await plus_minus_def(now=new_miq[2], price=new_miq[3]))
        else:
            await call.answer(text=f"Количество {data['food_name']} увеличено на 1.")
            await call.message.edit_reply_markup(reply_markup=await plus_minus_def_ru(now=new_miq[2], price=new_miq[3]))
    else:
        await add_product_to_basket(food_name=data['food_name'], narx=data['price'], chat_id=call.message.chat.id, menu_name=data['menu_name'])
        new_miq = await get_user_miqdor(chat_id=call.message.chat.id, fast_food=data['food_name'], menu_name=data['menu_name'])
        if lang[3] == "uz":
            await call.answer(text=f"{data['food_name']} Miqdori 1 taga oshirildi.")
            await call.message.edit_reply_markup(reply_markup=await plus_minus_def(now=new_miq[2], price=new_miq[3]))
        else:
            await call.answer(text=f"Количество {data['food_name']} увеличено на 1.")
            await call.message.edit_reply_markup(reply_markup=await plus_minus_def_ru(now=new_miq[2], price=new_miq[3]))

@dp.callback_query_handler(state='got_food', text=f"minus")
async def minus_handler(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.update_data({
        "food_name": data['food_name'],
        "menu_name": data['menu_name'],
        "price": data['price']
    })
    lang = await get_user(chat_id=call.message.chat.id)
    if await is_in_basket(food_name=data['food_name'], chat_id=call.message.chat.id, menu_name=data['menu_name']):
        old_miqdor = await get_product_in_basket(food_name=data['food_name'], chat_id=call.message.chat.id, menu_name=data['menu_name'])
        await update_product_miqdor_minus(miqdor=int(old_miqdor['miqdor']), product_name=data['food_name'], chat_id=call.message.chat.id, menu_name=data['menu_name'], now_price=int(old_miqdor['narx']))
        new_miq = await get_user_miqdor(chat_id=call.message.chat.id, fast_food=data['food_name'], menu_name=data['menu_name'])
        if lang[3] == "uz":
            await call.answer(text=f"✅ Mashulot 1 taga kamaydi")
        else:
            await call.answer(text=f"✅ Товар уменьшен на 1 шт.")

        menu_pic = await get_menu_pic(menu_name=data['menu_name'])
        try:
            if lang[3] == "uz":
                await call.message.edit_reply_markup(reply_markup=await plus_minus_def(now=int(new_miq['miqdor']), price=int(new_miq['narx'])))
            else:
                await call.message.edit_reply_markup(reply_markup=await plus_minus_def_ru(now=int(new_miq['miqdor']), price=int(new_miq['narx'])))
        except Exception as e:
            await call.message.delete()
            menuu = await get_fast_foods_in_menu(menu_name=data['menu_name'])
            menu_name = f""
            products = InlineKeyboardMarkup(row_width=2)

            for product in menuu:
                if lang[3] == "uz":
                    menu_name = f"😋 {product['menu']} Menyu"
                else:
                    menu_name = f"😋 {product['menu']} Меню"
                products.insert(InlineKeyboardButton(text=f"{product['food_name']}", callback_data=f"{product['food_name']}"))
            if lang[3] == "uz":
                products.insert(InlineKeyboardButton(text=f"⬅️ Ortga", callback_data='back_uz'))
                products.insert(InlineKeyboardButton(text=f"🏘 Asosiy menyu", callback_data='main_menu'))
            else:
                products.insert(InlineKeyboardButton(text=f"⬅️ Назад", callback_data='back_ru'))
                products.insert(InlineKeyboardButton(text=f"🏘 Главное меню", callback_data='back_main_menu_ru'))
            await call.message.answer_photo(photo=menu_pic['menu_picture'], caption=menu_name, reply_markup=products)
            await state.set_state('menu')
    else:
        if lang[3] == "uz":
            await call.answer(text=f"😕 Mahsulot kamida 1 dona bolishi kerak.")
        else:
            await call.answer(text=f"😕 Товара должно быть не менее 1 шт.")



@dp.message_handler(state="*", text=f"📥 Savat")
async def get_user_basket_handler(message: types.Message, state: FSMContext):
    user_basket = await get_user_basket(chat_id=message.chat.id)
    if user_basket:
        user_basket_bttn = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        user_basket_bttn.insert(KeyboardButton(text=f"🏘 Asosiy menyu"))
        user_basket_bttn.insert(KeyboardButton(text="🛍 Buyurtma berish"))
        userga = f"😊🛒 Sizning savatingiz.\n\n"
        total = 0
        for basket in user_basket:
            total += basket['narx']
            userga += f"<b>{basket['product']}</b> {int(basket['narx']) // int(basket['miqdor'])} * {basket['miqdor']} = {basket['narx']}\n"
            user_basket_bttn.insert(KeyboardButton(text=f"❌ {basket['product']}"))
        userga += f"💰 Ja'mi: <b>{total}</b>"
        await message.answer(text=userga, reply_markup=user_basket_bttn)
        await state.set_state('in_basket')
    else:
        userga = f"😕 Kechirasiz sizning savatingiz bosh."
        await message.answer(text=userga, reply_markup=main_menu_uzb)
        await state.finish()

@dp.message_handler(state="*", text=f"📥 Корзина")
async def get_user_basket_handler(message: types.Message, state: FSMContext):
    user_basket = await get_user_basket(chat_id=message.chat.id)
    if user_basket:
        user_basket_bttn = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        await state.set_state('in_basket')
        user_basket_bttn.insert(KeyboardButton(text=f"🏘 Главное меню"))
        user_basket_bttn.insert(KeyboardButton(text="🛍 Разместить заказ"))
        userga = f"😊🛒 Ваша Корзина.\n\n"
        total = 0
        for basket in user_basket:
            total += basket['narx']
            userga += f"<b>{basket['product']}</b> {int(basket['narx']) // int(basket['miqdor'])} * {basket['miqdor']} = {basket['narx']}\n"
            user_basket_bttn.insert(KeyboardButton(text=f"❌ {basket['product']}"))
        userga += f"\n\n💰 Общий: <b>{total}</b>"
        await message.answer(text=userga, reply_markup=user_basket_bttn)
    else:
        userga = f"😕 Извините, ваша корзина пуста."
        await message.answer(text=userga, reply_markup=main_menu_rus)
        await state.finish()

@dp.message_handler(text="⚙️ Sozlamalar")
async def settings_handler(message: types.Message, state: FSMContext):
    await message.answer(text=message.text, reply_markup=settings_uz)
    await state.set_state(f"setting")

@dp.message_handler(state="setting", text=f"👤 Ism Familyani O'zgartirish")
async def enter_new_name_handler(message: types.Message, state: FSMContext):
    userga = f"Toliq Ismingizni Kiriting."
    await message.answer(text=userga, reply_markup=cancel_uz)
    await state.set_state("new_name_uz")

@dp.message_handler(state="new_name_uz")
async def update_user_name_handler(message: types.Message, state: FSMContext):
    await update_user_name(chat_id=message.chat.id, new_name=message.text)
    userga = f"Ismingiz O'zgartirildi."
    await message.answer(text=userga, reply_markup=main_menu_uzb)
    await state.finish()

@dp.message_handler(state="setting", text=f"📞 Telefon Raqamni O'zgartirish")
async def set_phone_number_handler(message: types.Message, state: FSMContext):
    userga = f"📞 Iltimos Yangi Telefon Raqamingizni Kiriting."
    await message.answer(text=userga, reply_markup=cancel_uz)
    await state.set_state("set_number_uz")

@dp.message_handler(state="set_number_uz")
async def update_user_name_handler(message: types.Message, state: FSMContext):
    userga = f""
    if len(message.text) == 12 and message.text[0] != "+":
        userga = f"✅ Telefon Raqamingiz O'zgartirildi."
        await update_user_number(chat_id=message.chat.id, new_number=f"+{message.text}")
    elif len(message.text) == 13 and message.text[0] == "+":
        userga = f"✅ Telefon Raqamingiz O'zgartirildi."
        await update_user_number(chat_id=message.chat.id, new_number=f"{message.text}")
    elif len(message.text) == 9:
        userga = f"✅ Telefon Raqamingiz O'zgartirildi."
        await update_user_number(chat_id=message.chat.id, new_number=f"+998{message.text}")
    else:
        userga = f"❌ Telefon Raqamingizni Togri Kiriting.\nMasalan: <code>+998999999999</code>"
    await message.answer(text=userga, reply_markup=main_menu_uzb)
    await state.finish()

@dp.message_handler(state="setting", text=f"🇺🇿 🔁 🇷🇺 Tilni O'zgartirish")
async def set_phone_number_handler(message: types.Message, state: FSMContext):
    userga = f"Til Tanlang."
    await message.answer(text=f"Mavjud tillar", reply_markup=cancel_uz)
    await message.answer(text=userga, reply_markup=lang_select)
    await state.set_state("set_lang_uz")

@dp.callback_query_handler(state="set_lang_uz")
async def update_user_name_handler(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    if call.data == "uz":
        userga = f"✅ Muloqot Tili O'zgartirildi."
        await call.message.answer(text=userga, reply_markup=main_menu_uzb)
        await update_user_lang(chat_id=call.message.chat.id, new_lang=call.data)
    else:
        userga = f"✅ Язык общения изменен."
        await update_user_lang(chat_id=call.message.chat.id, new_lang=call.data)
        await call.message.answer(text=userga, reply_markup=main_menu_rus)
    await state.finish()

@dp.message_handler(text="⚙️ Настройки")
async def settings_handler(message: types.Message, state: FSMContext):
    await message.answer(text=message.text, reply_markup=settings_ru)
    await state.set_state(f"setting_ru")

@dp.message_handler(state="setting_ru", text=f"👤 Изменить имя Фамилию")
async def enter_new_name_handler(message: types.Message, state: FSMContext):
    userga = f"Введите свое полное имя."
    await message.answer(text=userga, reply_markup=cancel_rus)
    await state.set_state("new_name_ru")

@dp.message_handler(state="new_name_ru")
async def update_user_name_handler(message: types.Message, state: FSMContext):
    await update_user_name(chat_id=message.chat.id, new_name=message.text)
    userga = f"✅ Ваше имя изменено."
    await message.answer(text=userga, reply_markup=main_menu_rus)
    await state.finish()

@dp.message_handler(state="setting_ru", text=f"📞 Изменить номер телефона")
async def set_phone_number_handler(message: types.Message, state: FSMContext):
    userga = f"📞 Введите свой новый номер телефона."
    await message.answer(text=userga, reply_markup=cancel_rus)
    await state.set_state("set_number_ru")

@dp.message_handler(state="set_number_ru")
async def update_user_name_handler(message: types.Message, state: FSMContext):
    userga = f""
    if len(message.text) == 12 and message.text[0] != "+":
        userga = f"✅ Ваш номер телефона был изменен."
        await update_user_number(chat_id=message.chat.id, new_number=f"+{message.text}")
    elif len(message.text) == 13 and message.text[0] == "+":
        userga = f"✅ Ваш номер телефона был изменен."
        await update_user_number(chat_id=message.chat.id, new_number=f"{message.text}")
    elif len(message.text) == 9:
        userga = f"✅ Ваш номер телефона был изменен."
        await update_user_number(chat_id=message.chat.id, new_number=f"+998{message.text}")
    else:
        userga = f"❌ Введите свой номер телефона правильно.\n Например: <code>+998999999999</code>"
        await state.set_state("set_number_ru")
    await message.answer(text=userga, reply_markup=main_menu_rus)
    await state.finish()

@dp.message_handler(state="setting_ru", text=f"🇺🇿 🔁 🇷🇺 Изменить язык")
async def set_phone_number_handler(message: types.Message, state: FSMContext):
    await message.answer(text=f"Доступные языки", reply_markup=cancel_rus)
    userga = f"Выберите язык."
    await message.answer(text=userga, reply_markup=lang_select)
    await state.set_state("set_lang_ru")

@dp.callback_query_handler(state="set_lang_ru")
async def update_user_name_handler(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    if call.data == "uz":
        userga = f"✅ Muloqot Tili O'zgartirildi."
        await call.message.answer(text=userga, reply_markup=main_menu_uzb)
        await update_user_lang(chat_id=call.message.chat.id, new_lang=call.data)
    else:
        userga = f"✅ Язык общения изменен."
        await update_user_lang(chat_id=call.message.chat.id, new_lang=call.data)
        await call.message.answer(text=userga, reply_markup=main_menu_rus)
    await state.finish()

@dp.callback_query_handler(state='waiting_card', text='payed')
async def i_payed_card_handler(call: types.CallbackQuery, state: FSMContext):
    lang = await get_user(chat_id=call.message.chat.id)
    if lang[3] == "uz":
        userga = f"⚠️ Chekni rasmga olib tashlang."
    else:
        userga = f"⚠️ Отправьте фото чека"
    await call.message.answer(text=userga, reply_markup=ReplyKeyboardRemove())
    await state.set_state('send_screenshot')

@dp.message_handler(state='send_screenshot', content_types=types.ContentType.PHOTO)
async def sent_photo_to_curer_handler(message: types.Message, state: FSMContext):
    await state.update_data({
        'screenshot': message.photo[-1].file_id
    })
    data = await state.get_data()
    user = await get_user(chat_id=message.chat.id)
    lang = await get_user(chat_id=message.chat.id)
    userga = f""
    language = f""
    if user['lang'] == "uz":
        language = f"🇺🇿 Uzbek tili"
    else:
        language = f"🇷🇺 Rus tili"
    ishsiz_curer = await bosh_curer()
    random_number = random.randint(1000000, 1000000000)
    curerga = f"""
👤 To'liq ism: <b>{user['full_name']}</b>
👤 Username: <b>{user['username']}</b>
📞 Telefon raqam: <code>{user['phone_number']}</code>
🆔 Buyurtma raqami: {random_number}
🌐 Til: {language}
🛍 Mahsulotlar: \n
"""
    total = 0
    for product in await get_user_basket(chat_id=message.chat.id):
        await add_history_buys(chat_id=message.chat.id, number=random_number, miqdor=product['miqdor'],
                               product=product['product'], price=product['narx'] // product['miqdor'],
                               bought_at=message.date, status='Yetkazilmoqda', pay=data['pay'],
                               payment_status="To'langan", go_or_order='Buyurtma qilingan', which_filial='null')
        total += int(product['narx'])
        curerga += f"<b>{product['product']}</b> \t|\t <b>{product['miqdor']}</b> \t|\t <b>{product['narx'] // product['miqdor']}</b> * <b>{product['miqdor']}</b> = <b>{product['narx']}</b>\n"
    await update_user_status(chat_id=message.chat.id)
    curerga += f"💲 To'lov turi: {data['pay']}\n"
    curerga += f"💰 To'lov holati: <b>✅ To'langan</b>\n"
    curerga += f"➕ Ja'mi: {total}"
    bttn = InlineKeyboardMarkup(row_width=1)
    bttn.insert(InlineKeyboardButton(text=f"✅ Mahsulot yetkazildi", callback_data=f"{message.chat.id}a"))
    if ishsiz_curer:
        await dp.bot.send_photo(chat_id=ishsiz_curer['chat_id'], photo=data['screenshot'], caption=curerga)
        await dp.bot.send_location(chat_id=ishsiz_curer['chat_id'], latitude=data['latitude'], longitude=data['longitude'])
        if lang[3] == "uz":
            await message.answer(text=f"✅ Buyurtmangiz qabul qilindi.\n\n🆔 Buyurtma raqamingiz: {random_number}", reply_markup=main_menu_uzb)
        else:
            await message.answer(text=f"✅ Ваш заказ принят.\n\n🆔 Номер вашего заказа: {random_number}", reply_markup=main_menu_rus)
    else:
        all_curers = await get_all_curers()
        curers = []
        for curer in all_curers:
            curers.append(curer['chat_id'])
        random_curer = random.choice(curers)
        await dp.bot.send_photo(chat_id=random_curer, photo=data['screenshot'], caption=curerga)
        await dp.bot.send_location(chat_id=random_curer, latitude=data['latitude'],
                                   longitude=data['longitude'])
        if lang[3] == "uz":
            await message.answer(
                text=f"✅😔 Buyurtmangiz qabul qilindi ammo bo'sh kuryer topilmaganligi sabab buyurtmangiz ozgina kechikishi mumkin.Noqulayliklar uchun uzr so'raymiz",
                reply_markup=main_menu_uzb)
        else:
            await message.answer(
                text=f"✅😔 Ваш заказ принят, но доставка может немного задержаться, поскольку нам не удалось найти безработного курьера. Приносим извинения за неудобства",
                reply_markup=main_menu_uzb)


# Admin Functions

@dp.message_handler(text="⚙️🍴 Menyuni o'zgartirish")
async def set_menu_handler(message: types.Message, state: FSMContext):
    if await is_admin(chat_id=message.chat.id):
        adminga = f"Quyidagi bolimlardan birini tanlang."
        await message.answer(text=adminga, reply_markup=settings_menu)
        await state.set_state('setting')
    else:
        userga = f"😕 Kechirasiz: {message.from_user.full_name} siz adminlik huquqiga ega emassiz\n‼️ Bu funksiya faqat adminlar uchun!"
        await message.answer(text=userga, reply_markup=main_menu_uzb)
# Settings
@dp.message_handler(state="setting", text='➕🍴 Taom qoshish')
async def add_meal_to_menu_handler(message: types.Message, state: FSMContext):
    if await is_admin(chat_id=message.chat.id):
        adminga = '😊 Yangi taomni qaysi menyuga qoshmoqchisiz?'
        menuu = await get_menu()
        pic = await get_main_menu_logo()
        menu_bttn = InlineKeyboardMarkup(row_width=2)
        for meal in menuu:
            menu_bttn.insert(InlineKeyboardButton(text=f'{meal["menu_name"]}', callback_data=f'{meal["menu_name"]}'))
        menu_bttn.insert(InlineKeyboardButton(text=f'🏘 Asosiy menyu"', callback_data='main_menu'))
        await message.answer(text=adminga, reply_markup=cancel_uz)
        await message.answer_photo(photo=pic['photo'], reply_markup=menu_bttn)
        await state.set_state('select_menu')
    else:
        userga = f"😕 Kechirasiz: {message.from_user.full_name} siz adminlik huquqiga ega emassiz\n‼️ Bu funksiya faqat adminlar uchun!"
        await message.answer(text=userga, reply_markup=main_menu_uzb)

@dp.callback_query_handler(state='select_menu')
async def selecting_menu(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await state.update_data({
        "menu": call.data,
        "menu_ru": translate_uz_to_ru(text=call.data)
    })
    adminga = f"🖼 Yangi taomingizni rasmini yuboring"
    await call.message.answer(text=adminga, reply_markup=cancel_uz)
    await state.set_state('new_meal_pic')

@dp.message_handler(state='new_meal_pic', content_types=types.ContentType.PHOTO)
async def new_meal_picture_handler(message: types.Message, state: FSMContext):
    await state.update_data({
        "photo": message.photo[-1].file_id
    })
    adminga = f'✍️ Yangi taomni nomini yuboring.'
    await message.answer(text=adminga, reply_markup=cancel_uz)
    await state.set_state('enter_new_meal_name')

@dp.message_handler(state='enter_new_meal_name', content_types=types.ContentType.TEXT)
async def new_meal_name_handler(message: types.Message, state: FSMContext):
    await state.update_data({
        "name": message.text,
        "name_ru": translate_uz_to_ru(text=message.text)
    })
    adminga = f'💰 Yangi taomni narxini kiriting.\n‼️ Faqat Sonlarda'
    await message.answer(text=adminga, reply_markup=cancel_uz)
    await state.set_state('new_meal_price')

@dp.message_handler(state='new_meal_price')
async def new_meal_price_handler(message: types.Message, state: FSMContext):
    try:
        await state.update_data({
            "price": int(message.text)
        })

        adminga = f"✍️ Yangi taom haqida ma'lumot bering."
        await message.answer(text=adminga, reply_markup=cancel_uz)
        await state.set_state('description_new_meal')
    except ValueError:
        adminga = f"Kechirasiz yangi taomingiz narxini faqat raqamlarda kiriting!\nMasalan: <b>23000</b>"
        await message.answer(text=adminga, reply_markup=cancel_uz)
        await state.set_state('new_meal_price')
    except Exception as e:
        await dp.bot.send_message(chat_id=-1002075245072, text=f'Error: <b>{e}</b> Bot: Sobranie')
        adminga = f'😔 Kechirasiz botda xatolik yuz berdi.\nIltimos qayta urinib koring.'
        await message.answer(text=adminga, reply_markup=main_menu_uzb)
        await state.finish()

@dp.message_handler(state='description_new_meal')
async def get_new_meal_desc(message: types.Message, state: FSMContext):
    adminga = f''
    await state.update_data({
        "desc_uz": message.text,
        "desc_ru": translate_uz_to_ru(text=message.text)
    })
    try:
        data = await state.get_data()
        await add_meal_to_menu(data=data)
        await add_meal_to_menu_ru(data=data)
        adminga = f'✅ Yangi taom: <b>{data["menu"]}</b> menyusiga qoshildi!'
    except Exception as e:
        adminga = f"😔 Kechirasiz botda xatolik mavjud iltimos qayta urinib koring."
        await dp.bot.send_message(chat_id=-1002075245072, text=f'Error: <b>{e}</b> Bot: Sobranie')
    await message.answer(text=adminga, reply_markup=admins_panel)
    await state.finish()

@dp.message_handler(state='setting', text='🚫🍴 Taom olib tashlash')
async def delete_meal_in_menu_handler(message: types.Message, state: FSMContext):
    if await is_admin(chat_id=message.chat.id):
        adminga = f"😊 Qaysi menyudan taom olip tashlamoqchisiz?"
        pic = await get_main_menu_logo()
        menyu = await get_menu()
        menu_bttn = InlineKeyboardMarkup(row_width=2)
        for meal in menyu:
            menu_bttn.insert(InlineKeyboardButton(text=f"{meal['menu_name']}", callback_data=f"{meal['menu_name']}"))
        menu_bttn.insert(InlineKeyboardButton(text='🏘 Asosiy menyu', callback_data='main_menu'))
        await message.answer(text=adminga, reply_markup=cancel_uz)
        await message.answer_photo(photo=pic['photo'], reply_markup=menu_bttn)
        await state.set_state('selecting_menu_dl_ml')
    else:
        userga = f"😕 Kechirasiz: {message.from_user.full_name} siz adminlik huquqiga ega emassiz\n‼️ Bu funksiya faqat adminlar uchun!"
        await message.answer(text=userga, reply_markup=main_menu_uzb)

@dp.callback_query_handler(state='selecting_menu_dl_ml')
async def select_menu_dl_handler(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await state.update_data({
        'menu': call.data
    })
    foods_menu = InlineKeyboardMarkup(row_width=2)
    menu_foods = await get_fast_foods_in_menu(menu_name=call.data)
    for meal in menu_foods:
        foods_menu.insert(InlineKeyboardButton(text=f"{meal['fast_food_name']}", callback_data=f"{meal['fast_food_name']}"))
    foods_menu.insert(InlineKeyboardButton(text=f"🏘 Asosiy menyu", callback_data='main_menu'))
    await state.set_state('deleting')

@dp.callback_query_handler(state='deleting')
async def deleting_meal_handler(call: types.CallbackQuery, state: FSMContext):
    adminga = f"{await call.data} taomini haqiqatdan ham ochirib yubormoqchimisiz?"
    await call.message.answer(text=adminga, reply_markup=yes_no)
    await state.update_data({
        "meal": await call.data
    })
    await state.set_state('sure')

@dp.callback_query_handler(state='sure')
async def are_you_sure_handler(call: types.CallbackQuery, state: FSMContext):
    adminga = ""
    if await call.data == "yes":
        data = await state.get_data()
        await delete_meal(data=data)
        adminga = f'✅ {data["meal"]} Menyudan olip tashlandi!'
    else:
        adminga = f"❌ Bekor qilindi."
    await call.message.answer(text=adminga, reply_markup=admins_panel)
    await state.finish()

@dp.message_handler(state='setting', text="🍴➕ Yangi menyu qoshish")
async def add_new_menu_handler(message: types.Message, state: FSMContext):
    adminga = f"✍️ Yangi menyu nomini kiriting."
    await message.answer(text=adminga, reply_markup=cancel_uz)
    await state.set_state('enter_new_menu_name')

@dp.message_handler(state='enter_new_menu_name')
async def entering_new_menu_name_handler(message: types.Message, state: FSMContext):
    await state.update_data({
        "new_menu_name": message.text,
        "new_menu_name_ru": translate_uz_to_ru(text=message.text)
    })
    adminga = f'🖼 Yangi menyuni rasmini yuboring.'
    await message.answer(text=adminga, reply_markup=cancel_uz)
    await state.set_state('send_menu_pic')

@dp.message_handler(state='send_menu_pic', content_types=types.ContentType.PHOTO)
async def new_menu_pic_handler(message: types.Message, state: FSMContext):
    await state.update_data({
        "pic": message.photo[-1].file_id
    })
    data = await state.get_data()
    await add_new_menu(data=data)
    await add_new_menu_ru(data=data)
    adminga = f"✅ Yangi menyu qoshildi"
    await message.answer(text=adminga, reply_markup=admins_panel)
    await state.finish()

@dp.message_handler(state='setting', text="⚙️🍴 Menyu nomini o'zgartirish")
async def edit_menu_name_handler(message: types.Message, state: FSMContext):
    adminga = f"Qaysi menyuni nomini o'zgartirmoqchisiz?"
    menu_bttn = InlineKeyboardMarkup(row_width=2)
    pic = await get_main_menu_logo()
    all_menu = await get_menu()
    for meal in all_menu:
        menu_bttn.insert(InlineKeyboardButton(text=f'{meal["food_name"]}', callback_data=f"{meal['food_name']}"))
    menu_bttn.insert(InlineKeyboardButton(text=f"🏘 Asosiy menyu", callback_data='main_menu'))
    await message.answer(text=adminga, reply_markup=cancel_uz)
    await message.answer_photo(photo=pic['photo'], reply_markup=menu_bttn)
    await state.set_state('set_name')

@dp.callback_query_handler(state='set_name')
async def setting_name_handler(call: types.CallbackQuery, state: FSMContext):
    await state.update_data({
        "menu": await call.data,
        "menu_ru": translate_uz_to_ru(text=f"{await call.data}")
    })
    await call.message.delete()
    adminga = f"✍️ {await call.data} menuning yangi nomini kiriting"
    await call.message.answer(text=adminga, reply_markup=cancel_uz)
    await state.set_state('new_name')

@dp.message_handler(state='new_name')
async def setting_name_handler(message: types.Message, state: FSMContext):
    await state.update_data({
        "new_name": message.text,
        "new_name_ru": translate_uz_to_ru(text=f"{message.text}")
    })
    data = await state.get_data()
    await update_menu_name_ru(data=data)
    await update_menu_name_(data=data)
    await update_menu_name(data=data)
    await update_menu_name_ru_(data=data)
    data = await state.get_data()
    adminga = f"✅ {data['menu']} menyu nomi: {message.text}ga ozgartirildi!"
    await message.answer(text=adminga, reply_markup=cancel_uz)
    await state.finish()

@dp.message_handler(state='setting', text='🚫🍴 Menyu ochirish')
async def delete_menu_handler(message: types.Message, state: FSMContext):
    adminga = f"Qaysi menyuni ochirib yubormoqchisiz?"
    menus = await get_menu()
    menu_bttn = InlineKeyboardMarkup(row_width=2)
    for menuu in menus:
        menu_bttn.insert(InlineKeyboardButton(text=f'{menuu["menu_name"]}', callback_data=f"{menuu['menu_name']}"))
    menu_bttn.insert(InlineKeyboardButton(text=f"❌ Bekor Qilish", callback_data='cancel_uz'))
    await message.answer(text=adminga, reply_markup=menu_bttn)
    await state.set_state('selecting_menu_to_delete')

@dp.callback_query_handler(state='selecting_menu_to_delete')
async def delete_menu_handler(call: types.CallbackQuery, state: FSMContext):
    await state.update_data({
        "menu": call.data,
        'rus_menu_name': translate_uz_to_ru(text=call.data)
    })
    adminga = f"{call.data} menyuni va menyudagi taomlarni haqiqatdan ochirib yubormoqchimisiz?"
    await call.message.answer(text=adminga, reply_markup=yes_no)
    await state.set_state('sure_to_del_menu')

@dp.callback_query_handler(state='sure_to_del_menu')
async def really_del_menu_handler(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    adminga = f""
    if call.data == "yes":
        data = await state.get_data()
        await delete_menu(menu_name=data['menu'], rus_menu_name=data['rus_menu_name'])
        adminga = f"✅ Menyu bolimidan: {data['menu']} ochirildi."
    else:
        adminga = f"✅ Bekor qilindi."
    await call.message.answer(text=adminga, reply_markup=admins_panel)
    await state.finish()

@dp.message_handler(state='setting', text=f"🔧💰 Taom narxini o'zgartirish")
async def edit_meal_price_handler(message: types.Message, state: FSMContext):
    if await is_admin(chat_id=message.chat.id):
        adminga1 = f"Quyidagilardan birini tanlang."
        adminga = f"😊 Qaysi menyudagi taom narxini o'zgartirmoqchisiz?"
        menu_bttn = InlineKeyboardMarkup(row_width=2)
        for menyu in await get_menu():
            menu_bttn.insert(InlineKeyboardButton(text=f"{menyu['menu_name']}", callback_data=f"{menyu['menu_name']}"))
        menu_bttn.insert(InlineKeyboardButton(text=f"❌ Bekor Qilish", callback_data='main_menu'))
        await message.answer(text=adminga1, reply_markup=cancel_uz)
        await message.answer(text=adminga, reply_markup=menu_bttn)
        await state.set_state('select_menu_price')
    else:
        userga = f"Kechirasiz: {message.from_user.full_name} siz adminlik huquqiga ega emassiz.\nBu funksiya faqat adminlar uchun!"
        await message.answer(text=userga, reply_markup=main_menu_uzb)
        await state.finish()

@dp.callback_query_handler(state="select_menu_price")
async def select_menu_handler(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await state.update_data({
        "menu": call.data,
        "menu_ru": translate_uz_to_ru(text=call.data)
    })
    adminga = f"{call.data} menyudagi qaysi taom narxini o'zgartirmoqchisiz?"
    meals = InlineKeyboardMarkup(row_width=2)
    for meal in await get_fast_foods_in_menu(menu_name=call.data):
        meals.insert(InlineKeyboardButton(text=f"{meal['food_name']}", callback_data=f"{meal['food_name']}"))
    meals.insert(InlineKeyboardButton(text=f"❌ Bekor Qilish", callback_data='main_menu'))
    await call.message.answer(text=adminga, reply_markup=meals)
    await state.set_state('select_meal')

@dp.callback_query_handler(state='select_meal')
async def selecting_meal_handler(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    data = await state.get_data()
    await state.update_data({
        "menu": data['menu'],
        "menu_ru": data['menu_ru'],
        'food_name': call.data
    })
    food = await get_fast_food_in_menu(fast_food_name=call.data, menu_name=data['menu'])
    await call.message.answer_photo(photo=food['photo'], caption=f"Mahsulot: {food['food_name']}\nNarxi: {food['price']}")
    adminga = f"💸 {food['food_name']} uchun yangi narx kiriting.\n‼️ Faqat sonlarda masalan: <b>23000</b>"
    await call.message.answer(text=adminga, reply_markup=cancel_uz)
    await state.set_state('new_price_meal')

@dp.message_handler(state='new_price_meal')
async def updating_meal_price_handler(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        await update_meal_price(new_price=int(message.text), menu_name=data['menu'], rus_menu_name=data['menu_ru'], food_name=data['food_name'])
        adminga = f"<b>{data['food_name']}</b> mahsulotining narxi {message.text} ga o'zgartirildi."
        await message.answer(text=adminga, reply_markup=admins_panel)
        await state.finish()
    except ValueError:
        adminga = f"😕 Kechirasiz siz noto'gri narx kiritdingiz narxni faqat sonlarda kiritishingiz mumkin.\nMasaln: 23000"
        await message.answer(text=adminga, reply_markup=cancel_uz)
        await state.set_state('new_price_meal')
    except Exception as e:
        
        await dp.bot.send_message(chat_id=-1002075245072, text=f"Error: <b>{e}</b> Bot: <b>Sobranie</b>")
        adminga = f"😕 Kechirasiz botda xatolik mavjud iltimos qayta urinib koring."
        await message.answer(text=adminga, reply_markup=admins_panel)
        await state.finish()

@dp.message_handler(state='setting', text=f"🔧🖼 Taom rasmini o'zgartirish")
async def edit_meal_price_handler(message: types.Message, state: FSMContext):
    if await is_admin(chat_id=message.chat.id):
        adminga1 = f"Quyidagilardan birini tanlang."
        adminga = f"😊 Qaysi menyudagi taom rasmini o'zgartirmoqchisiz?"
        menu_bttn = InlineKeyboardMarkup(row_width=2)
        for menyu in await get_menu():
            menu_bttn.insert(InlineKeyboardButton(text=f"{menyu['menu_name']}", callback_data=f"{menyu['menu_name']}"))
        menu_bttn.insert(InlineKeyboardButton(text=f"❌ Bekor Qilish", callback_data='main_menu'))
        await message.answer(text=adminga1, reply_markup=cancel_uz)
        await message.answer(text=adminga, reply_markup=menu_bttn)
        await state.set_state('select_menu_photo')
    else:
        userga = f"Kechirasiz: {message.from_user.full_name} siz adminlik huquqiga ega emassiz.\nBu funksiya faqat adminlar uchun!"
        await message.answer(text=userga, reply_markup=main_menu_uzb)
        await state.finish()

@dp.callback_query_handler(state="select_menu_photo")
async def select_menu_handler(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await state.update_data({
        "menu": call.data,
        "menu_ru": translate_uz_to_ru(text=call.data)
    })
    adminga = f"{call.data} menyudagi qaysi taom rasmini o'zgartirmoqchisiz?"
    meals = InlineKeyboardMarkup(row_width=2)
    for meal in await get_fast_foods_in_menu(menu_name=call.data):
        meals.insert(InlineKeyboardButton(text=f"{meal['food_name']}", callback_data=f"{meal['food_name']}"))
    meals.insert(InlineKeyboardButton(text=f"❌ Bekor Qilish", callback_data='main_menu'))
    await call.message.answer(text=adminga, reply_markup=meals)
    await state.set_state('select_meal_to_photo')

@dp.callback_query_handler(state='select_meal_to_photo')
async def selecting_meal_handler(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    data = await state.get_data()
    await state.update_data({
        "menu": data['menu'],
        "menu_ru": data['menu_ru'],
        'food_name': call.data
    })
    adminga = f"🖼 Ushbu taom uchun yangi rasmni yuboring"
    await call.message.answer(text=adminga, reply_markup=cancel_uz)
    await state.set_state('new_photo_meal')

@dp.message_handler(state='new_photo_meal', content_types=types.ContentType.PHOTO)
async def updating_meal_price_handler(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        await update_meal_photo(new_photo=message.photo[-1].file_id, menu_name=data['menu'], rus_menu_name=data['menu_ru'], food_name=data['food_name'])
        adminga = f"✅ <b>{data['food_name']}</b> mahsulotining rasmi o'zgartirildi."
        await message.answer(text=adminga, reply_markup=admins_panel)
        await state.finish()

    except Exception as e:
        await dp.bot.send_message(chat_id=-1002075245072, text=f"Error: <b>{e}</b> Bot: <b>Sobranie</b>")
        adminga = f"😕 Kechirasiz botda xatolik mavjud iltimos qayta urinib koring."
        await message.answer(text=adminga, reply_markup=admins_panel)
        await state.finish()

@dp.message_handler(state='setting', text=f"🔧✍️ Taom nomini o'zgartirish")
async def edit_meal_price_handler(message: types.Message, state: FSMContext):
    if await is_admin(chat_id=message.chat.id):
        adminga1 = f"Quyidagilardan birini tanlang."
        adminga = f"😊 Qaysi menyudagi taom nomini o'zgartirmoqchisiz?"
        menu_bttn = InlineKeyboardMarkup(row_width=2)
        for menyu in await get_menu():
            menu_bttn.insert(InlineKeyboardButton(text=f"{menyu['menu_name']}", callback_data=f"{menyu['menu_name']}"))
        menu_bttn.insert(InlineKeyboardButton(text=f"❌ Bekor Qilish", callback_data='main_menu'))
        await message.answer(text=adminga1, reply_markup=cancel_uz)
        await message.answer(text=adminga, reply_markup=menu_bttn)
        await state.set_state('select_menu_name')
    else:
        userga = f"😕 Kechirasiz: {message.from_user.full_name} siz adminlik huquqiga ega emassiz.\nBu funksiya faqat adminlar uchun!"
        await message.answer(text=userga, reply_markup=main_menu_uzb)
        await state.finish()

@dp.callback_query_handler(state="select_menu_name")
async def select_menu_handler(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await state.update_data({
        "menu": call.data,
        "menu_ru": translate_uz_to_ru(text=call.data)
    })
    adminga = f"‼️ {call.data} menyudagi qaysi taom nomini o'zgartirmoqchisiz?"
    meals = InlineKeyboardMarkup(row_width=2)
    for meal in await get_fast_foods_in_menu(menu_name=call.data):
        meals.insert(InlineKeyboardButton(text=f"{meal['food_name']}", callback_data=f"{meal['food_name']}"))
    meals.insert(InlineKeyboardButton(text=f"❌ Bekor Qilish", callback_data='main_menu'))
    await call.message.answer(text=adminga, reply_markup=meals)
    await state.set_state('select_meal_to_name')

@dp.callback_query_handler(state='select_meal_to_name')
async def selecting_meal_handler(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    data = await state.get_data()
    await state.update_data({
        "menu": data['menu'],
        "menu_ru": data['menu_ru'],
        'food_name': call.data
    })
    adminga = f"✍️ Ushbu taomni yangi nomini yuboring"
    await call.message.answer(text=adminga, reply_markup=cancel_uz)
    await state.set_state('new_name_meal')

@dp.message_handler(state='new_name_meal', content_types=types.ContentType.TEXT)
async def updating_meal_price_handler(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        await update_meal_name(new_name=message.text, menu_name=data['menu'], rus_menu_name=data['menu_ru'], food_name=data['food_name'])
        adminga = f"✅ <b>{data['food_name']}</b> mahsulotining nomi o'zgartirildi."
        await message.answer(text=adminga, reply_markup=admins_panel)
        await state.finish()

    except Exception as e:
        await dp.bot.send_message(chat_id=-1002075245072, text=f"Error: <b>{e}</b> Bot: <b>Sobranie</b>")
        adminga = f"😕 Kechirasiz botda xatolik mavjud iltimos qayta urinib koring."
        await message.answer(text=adminga, reply_markup=admins_panel)
        await state.finish()

@dp.message_handler(text="👤 Adminlar")
async def admin_handler(message: types.Message, state: FSMContext):
    if await is_admin(chat_id=message.chat.id):
        adminga = f"Quyidagilardan birini tanlang."
        await message.answer(text=adminga, reply_markup=admins_settings)
        await state.set_state("setting_admin")
    else:
        userga = f"😕 Kechirasiz siz adminlik xuquqiga ega emassiz!\nBu funksiya faqat adminlar uchun!"
        await message.answer(text=userga, reply_markup=main_menu_uzb)

@dp.message_handler(state="setting_admin", text="➕👤 Yangi admin qoshish")
async def admin_handler(message: types.Message, state: FSMContext):
    if await is_admin(chat_id=message.chat.id):
        adminga = f"😊 Yangi admin <b>CHAT ID</b> raqamini kiriting."
        await message.answer(text=adminga, reply_markup=cancel_uz)
        await state.set_state("sending_admin_chat_id")
    else:
        userga = f"😕 Kechirasiz siz adminlik xuquqiga ega emassiz!\nBu funksiya faqat adminlar uchun!"
        await message.answer(text=userga, reply_markup=main_menu_uzb)

@dp.message_handler(state="sending_admin_chat_id")
async def admin_handler(message: types.Message, state: FSMContext):
    try:
        await state.update_data({
            "chat_id": int(message.text)
        })
        adminga = f"✍️ Yangi adminning ismini kiriting"
        await message.answer(text=adminga, reply_markup=cancel_uz)
        await state.set_state("get_admin_name")
    except ValueError:
        adminga = "😕 Kechirasiz yangi admin <b>CHAT ID</b> raqamini faqat butun sonlarda kiritishingiz mumkin!"
        await message.answer(text=adminga, reply_markup=cancel_uz)
        await state.set_state('sending_admin_chat_id')

@dp.message_handler(state='get_admin_name')
async def got_admin_name_handler(message: types.Message, state: FSMContext):
    try:
        await state.update_data({
            "name": message.text
        })
        data = await state.get_data()
        await add_admin_to_db(data=data)
        await dp.bot.send_message(chat_id=data['chat_id'], text=f"🥳 Tabriklaymiz: {message.text} siz ushbu botda adminlik huquqiga ega boldingiz!", reply_markup=admins_panel)
        await message.answer(text=f"🥳 Tabriklaymiz yangi admin adminlar bolimiga qoshildi!", reply_markup=admins_panel)
        await state.finish()
    except Exception as e:
        adminga = f"😕 Kechirasiz botda xatolik yuz berdi iltimos qayta urunib koring!"
        await dp.bot.send_message(chat_id=-1002075245072, text=f"Error: <b>{e}</b> Line 649")
        await message.answer(text=adminga, reply_markup=admins_panel)
        await state.finish()

@dp.message_handler(state='setting_admin', text=f"🚫👤 Admin olib tashlash")
async def remove_admin_handler(message: types.Message, state: FSMContext):
    if await is_admin(chat_id=message.chat.id):
        adminga = ""
        all_admins = await get_all_admins()
        for admin in all_admins:
            adminga += f"🆔 Chat_id: <code>{admin['chat_id']}</code> 👤 Ism: <b>{admin['name']}</b>\n"
        adminga += f"Olib tashlamoqchi bolgan adminingiz <b>CHAT ID</b> raqamini kiriting!"
        await message.answer(text=adminga, reply_markup=cancel_uz)
        await state.set_state('getting_chatid_dl')
    else:
        userga = f"😕 Kechirasiz: {message.from_user.full_name} siz adminlik huquqiga ega emassiz bu funksiya faqat bot adminlari uchun"
        await message.answer(text=userga, reply_markup=main_menu_uzb)
        await state.finish()

@dp.message_handler(state='getting_chatid_dl')
async def got_admin_chat_id_handler(message: types.Message, state: FSMContext):
    try:
        adminga = f"👍 Ushbu admin adminlar orasidan olib tashlandi."
        await dp.bot.send_message(chat_id=int(message.text), text=f'😕 Kechirasiz siz adminlar orasidan olib tashlandingiz.', reply_markup=main_menu_uzb)
        await dl_admin(chat_id=int(message.chat.id))
        await message.answer(text=adminga, reply_markup=admins_panel)
        await state.finish()
    except ValueError:
        adminga = f"😕 Kechirasiz admin chat_id raqamini faqat sonlarda kiritish mumkin!"
        await message.answer(text=adminga, reply_markup=cancel_uz)
        await state.set_state('getting_chatid_dl')
    except Exception as e:
        await dp.bot.send_message(chat_id=-1002075245072, text=f"Error: <b>{e}</b> Line 680 Bot Sobranie")
        adminga = f"😕 Kechirasiz botda xatolik yuz berdi iltimos qayta urinib koring!"
        await message.answer(text=adminga, reply_markup=admins_panel)
        await state.finish()

@dp.message_handler(state='setting_admin', text=f"📄👤 Adminlar")
async def get_all_admins_handler(message: types.Message, state: FSMContext):
    if await is_admin(chat_id=message.chat.id):
        adminga = f"Ushbu botdagi barcha adminlar ro'yxati.\n\n"
        all_admins = await get_all_admins()
        for admin in all_admins:
            adminga += f"🆔 Chat_id: <code>{admin['chat_id']}</code> 👤 Ism: {admin['name']}\n"
        await message.answer(text=adminga, reply_markup=admins_panel)
    else:
        userga = f"😕 Kechirasiz: {message.from_user.full_name} siz adminlik huquqiga ega emassiz bu funksiya faqat bot adminlari uchun"
        await message.answer(text=userga, reply_markup=main_menu_uzb)
    await state.finish()

@dp.message_handler(text="🚚 Kuryerlar")
async def curers_handler(message: types.Message, state: FSMContext):
    if await is_admin(chat_id=message.chat.id):
        adminga = f"Quyidagi bolimdan birini tanlang."
        await message.answer(text=adminga, reply_markup=curers)
        await state.set_state('setting_curer')
    else:
        userga = f"😕 Kechirasiz: {message.from_user.full_name} siz adminlik huquqiga ega emassiz bu funksiya faqat bot adminlari uchun"
        await message.answer(text=userga, reply_markup=main_menu_uzb)
        await state.finish()

@dp.message_handler(state='setting_curer')
async def setting_curer_handler(message: types.Message, state: FSMContext):
    if message.text[0] == "➕":
        await message.answer(text=f"✍️ Yangi kuryer ismini kiriting.", reply_markup=cancel_uz)
        await state.set_state('get_new_curer_name')
    elif message.text[0] == "🚫":
        await message.answer(text=f"✍️ Ochirib yubormoqchi bolgan kuryer chat_id raqamini kiriting yoki ismini kiriting.", reply_markup=cancel_uz)
        await state.set_state('get_delete_curer_name')
    elif message.text[0] == "📄":
        adminga = f"Kuryerlar ro'yxati.\n"
        all_curers = await get_all_curers()
        for curer in all_curers:
            adminga += f"👤 Ism: {curer['name']} \t Chat_id: {curer['chat_id']}"
        await message.answer(text=adminga)

@dp.message_handler(state="get_new_curer_name")
async def get_new_curer_name_handler(message: types.Message, state: FSMContext):
    adminga = 'Yangi kuryer <b>CHAT ID</b> raqamini kiriting!'
    await message.answer(text=adminga, reply_markup=cancel_uz)
    await state.update_data({
        "name": message.text.capitalize()
    })
    await state.set_state('get_new_curer_id')

@dp.message_handler(state="get_new_curer_id")
async def get_new_curer_name_handler(message: types.Message, state: FSMContext):
    try:
        await state.update_data({
            "chat_id": int(message.text)
        })
        data = await state.get_data()
        await insert_curer(data=data)
        adminga = f"🥳 Tabriklaymiz yangi kuryer qoshildi."
        await message.answer(text=adminga, reply_markup=admins_panel)
        await state.finish()
    except ValueError:
        adminga = f"Kechirasiz siz yangi kuryer <b>CHAT ID</b> raqamini sonlarda kiritmadingiz!"
        await message.answer(text=adminga, reply_markup=cancel_uz)
        await state.set_state("get_new_curer_id")
    except Exception as e:
        await dp.bot.send_message(chat_id=-1002075245072, text=f"Error: <b>{e}</b> Bot: Sobranie")
        await message.answer(text=f"😕 Kechirasiz bu chat_id raqamdagi foydalnuvchi botdan topilmadi!")
        await state.finish()

@dp.message_handler(state='get_delete_curer_name')
async def get_delete_curer_name_handler(message: types.Message, state: FSMContext):
    adminga = f""
    if message.text.isdigit():
        adminga = f"⚠️⚠️ Haqiqatdan ham ushbu chat id raqamdagi kuryerni ochirib yubormoqchimisiz?"
    else:
        adminga = f"⚠️⚠️ Haqiqatdan ham: {message.text} ismli kuryerni ochirib yubormoqchimisiz?"
    await state.update_data({
        "name": message.text
    })
    await message.answer(text=adminga, reply_markup=yes_no_def)
    await state.set_state('really_del')

@dp.message_handler(text=f"💸 To'lov turlarini o'zgartirish.")
async def change_payment_methods_handler(message: types.Message, state: FSMContext):
    if await is_admin(chat_id=message.chat.id):
        adminga = f"😊 Quyidagilardan birini tanlang."
        await message.answer(text=adminga, reply_markup=payment_settings)
        await state.set_state('setting_payment')
    else:
        userga = f"😕 Kechirasiz: {message.from_user.full_name} siz adminlik huquqiga ega emassiz bu funksiya faqat bot adminlari uchun"
        await message.answer(text=userga, reply_markup=main_menu_uzb)
        await state.finish()

@dp.message_handler(state='setting_payment')
async def payment_method_handler(message: types.Message, state: FSMContext):
    payments = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    for payment in await select_payments():
        payments.insert(KeyboardButton(text=f"{payment['payment_name']}"))
    payments.insert(KeyboardButton(text=f"❌ Bekor Qilish"))
    if message.text[0] == "🚫":
        adminga = f"😊 Qaysi tolov turini ochirib qoymoqchisiz?"
        await message.answer(text=adminga, reply_markup=payments)
        await state.set_state('turning_off_payment')
    elif message.text[0] == "➕":
        adminga = f"✍️ Yangi tolov turini nomini kiriting."
        await message.answer(text=adminga, reply_markup=cancel_uz)
        await state.set_state('new_payment_method_name')
    elif message.text[0] == "🗑":
        adminga = f"😊 Qaysi tolov turini ochirib tashlamoqchisiz?"
        await message.answer(text=adminga, reply_markup=payments)
        await state.set_state('deleting_payment')
    elif message.text[0] == "👍":
        false_payments_bttn = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        adminga = f""
        if await false_payments():
            for false_pay in await false_payments():
                false_payments_bttn.insert(KeyboardButton(false_pay['payment_name']))
            false_payments_bttn.insert(KeyboardButton(text=f"❌ Bekor Qilish"))
            adminga = f"⚙️ Qaysi tolov holatini o'zgartirmoqchisiz?"
            await message.answer(text=adminga, reply_markup=false_payments_bttn)
            await state.set_state('change_payment_status')
        else:
            adminga = f"😕 Holati o'chirilgan tolov turlari yo'q"
            await message.answer(text=adminga, reply_markup=admins_panel)
            await state.finish()
    else:
        adminga = f"😕 Bunday funksiya topilmadi."
        await message.answer(text=adminga, reply_markup=admins_panel)
        await state.finish()

@dp.message_handler(state='turning_off_payment')
async def turning_off_handler(message: types.Message, state: FSMContext):
    adminga = f""
    try:
        await turning_off_payment(payment_name=message.text)
        adminga = f"✅ {message.text} tolov turi holati ochirildi."
    except Exception as e:
        await dp.bot.send_message(chat_id=-1002075245072, text=f"Error: <b>{e}</b> Bot: Sobranie")
        adminga = f"❌ Kechirasiz botda xatolik yuz berdi iltimos qayta urinib ko'ring."
    await state.finish()
    await message.answer(text=adminga, reply_markup=admins_panel)

@dp.message_handler(state='new_payment_method_name')
async def turning_off_handler(message: types.Message, state: FSMContext):
    adminga = f""
    try:
        await add_payment_method(new_payment_name=message.text)
        adminga = f"🥳 Yangi to'lov turi qoshildi"
    except Exception as e:
        await dp.bot.send_message(chat_id=-1002075245072, text=f"Error: <b>{e}</b> Bot: <b>Sobranie</b>")
        adminga = f"😔 Kechirasiz botda xatolik yuz berdi iltimos qayta urinib ko'ring."
    await message.answer(text=adminga, reply_markup=admins_panel)
    await state.finish()

@dp.message_handler(state='deleting_payment')
async def turning_off_handler(message: types.Message, state: FSMContext):
    adminga = f""
    try:
        await delete_payment(payment_name=message.text)
        adminga = f"✅ Ushbu to'lov turi ochirib yuborildi."
    except Exception as e:
        await dp.bot.send_message(chat_id=-1002075245072, text=f"Error: <b>{e}</b> Bot: <b>Sobranie</b>")
        adminga = f"😔 Kechirasiz botda xatolik yuz berdi iltimos qayta urinib ko'ring."
    await message.answer(text=adminga, reply_markup=admins_panel)
    await state.finish()

@dp.message_handler(state='change_payment_status')
async def turning_off_handler(message: types.Message, state: FSMContext):
    adminga = f""
    try:
        await update_payment_status(payment_name=message.text)
        adminga = f"✅ Ushbu to'lov turi holati yondi."
    except Exception as e:
        await dp.bot.send_message(chat_id=-1002075245072, text=f"Error: <b>{e}</b> Bot: <b>Sobranie</b>")
        adminga = f"😔 Kechirasiz botda xatolik yuz berdi iltimos qayta urinib ko'ring."
    await message.answer(text=adminga, reply_markup=admins_panel)
    await state.finish()

@dp.message_handler(state='really_del')
async def get_delete_curer_name_handler(message: types.Message, state: FSMContext):
    adminga = f""
    data = await state.get_data()
    if message.text == "✅ Xa":
        if await del_curer(data=data):
            adminga = f"✅ Kuryer olib tashlandi."
        else:
            adminga = f"😕 Kechirasiz bu chat_id raqamdagi foydalnuvchi botdan topilmadi!"
    else:
        adminga = f"{message.text[0]} Bekor qilindi."
    await state.finish()
    await message.answer(text=adminga, reply_markup=admins_panel)

@dp.message_handler(state='waiting_card')
async def user_dont_want_wait_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user = await get_user(chat_id=message.chat.id)
    lang = await get_user(chat_id=message.chat.id)
    userga = f""
    language = f""
    if user['lang'] == "uz":
        language = f"🇺🇿 Uzbek tili"
    else:
        language = f"🇷🇺 Rus tili"
    ishsiz_curer = await bosh_curer()
    random_number = random.randint(1000000, 1000000000)
    curerga = f"""
👤 To'liq ism: <b>{user['full_name']}</b>
👤 Username: <b>{user['username']}</b>
📞 Telefon raqam: <code>{user['phone_number']}</code>
🆔 Buyurtma raqami: {random_number}
🌐 Til: {language}
🛍 Mahsulotlar: \n
"""
    total = 0
    for product in await get_user_basket(chat_id=message.chat.id):
        await add_history_buys(chat_id=message.chat.id, number=random_number, miqdor=product['miqdor'],
                               product=product['product'], price=product['narx'] // product['miqdor'],
                               bought_at=message.date, status='Yetkazilmoqda', pay=data['pay'],
                               payment_status="To'lanmagan", go_or_order='Buyurtma qilingan', which_filial='null')
        total += int(product['narx'])
        curerga += f"<b>{product['product']}</b> \t|\t <b>{product['miqdor']}</b> \t|\t <b>{product['narx'] // product['miqdor']}</b> * <b>{product['miqdor']}</b> = <b>{product['narx']}</b>\n"
    await update_user_status(chat_id=message.chat.id)
    curerga += f"💲 To'lov turi: {data['pay']}\n"
    curerga += f"💰 To'lov holati: <b>❌ To'lanmagan</b>\n"
    curerga += f"<b>💳 Plastik karta kutyabdi</b>\n"
    curerga += f"➕ Ja'mi: {total}"
    bttn = InlineKeyboardMarkup(row_width=1)
    bttn.insert(InlineKeyboardButton(text=f"✅ Mahsulot yetkazildi", callback_data=f"{message.chat.id}_{random_number}_curer"))
    if ishsiz_curer:
        await update_curer_status(chat_id=ishsiz_curer['chat_id'])
        await dp.bot.send_message(chat_id=ishsiz_curer['chat_id'], text=curerga, reply_markup=bttn)
        await dp.bot.send_location(chat_id=ishsiz_curer['chat_id'], longitude=data['longitude'], latitude=data['latitude'])
        if lang[3] == "uz":
            await message.answer(text=f"✅ Buyurtmangiz qabul qilindi.", reply_markup=main_menu_uzb)
        else:
            await message.answer(text=f"✅ Ваш заказ принят.", reply_markup=main_menu_rus)
    else:
        curers_list = []
        for curer in await get_all_curers():
            curers_list.append(curer['chat_id'])
        random_curer = random.choice(curers_list)
        await dp.bot.send_location(chat_id=int(random_curer), longitude=data['longitude'], latitude=data['latitude'])
        await dp.bot.send_message(chat_id=int(random_curer), text=curerga, reply_markup=bttn)
        await add_count_to_curer(chat_id=random_curer)
        if lang[3] == "uz":
            await message.answer(
                text=f"✅😕 Buyurtmangiz qabul qilindi ammo bo'sh kuryer topilmaganligi sabab buyurtmangiz ozgina kechikishi mumkin.Noqulayliklar uchun uzr so'raymiz",
                reply_markup=main_menu_uzb)
        else:
            await message.answer(
                text=f"✅😕 Ваш заказ принят, но доставка может немного задержаться, поскольку нам не удалось найти безработного курьера. Приносим извинения за неудобства",
                reply_markup=main_menu_uzb)
    await state.finish()

@dp.message_handler(state='in_basket')
async def dl_from_basket_handler(message: types.Message, state: FSMContext):
    if message.text[0] == "❌":
        await delete_product_from_basket(chat_id=message.chat.id, product=message.text[2:])
        lang = await get_user(chat_id=message.chat.id)
        if lang[3] == "uz":
            userga = f"✅ {message.text[2:]} savatingizdan olib tashlandi."
            await message.answer(text=userga, reply_markup=main_menu_uzb)
        else:
            userga = f"✅ {message.text[2:]} был удален из вашей корзины."
            await message.answer(text=userga, reply_markup=main_menu_rus)
        await state.finish()
    else:
        lang = await get_user(chat_id=message.chat.id)
        if lang[3] == "uz":
            userga = f"😊 Asosiy menyu"
            await message.answer(text=userga, reply_markup=main_menu_uzb)
        else:
            userga = "😊 Главное меню"
            await message.answer(text=userga, reply_markup=main_menu_rus)

