import random
from datetime import timedelta

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
    if lang['lang'] == "uz":
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
    menyu_ru.insert(InlineKeyboardButton(text='🏘 Главное меню', callback_data='main_menu'))
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
            meals.insert(InlineKeyboardButton(text=f'⬅️ Ortga', callback_data=f'back_to_menu_uz'))
            meals.insert(InlineKeyboardButton(text=f"🏘 Asosiy menyu", callback_data='main_menu'))
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
            meals.insert(InlineKeyboardButton(text=f'⬅️ Назад', callback_data=f'back_to_menu_ru'))
            meals.insert(InlineKeyboardButton(text=f'🏘 Главное меню', callback_data='main_menu'))
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
            await call.message.answer_photo(photo=photo, caption=userga, reply_markup=await plus_minus_def(0, 0, back_bttn=fast_food['menu']))
        else:
            userga = f"""
😋 {food_name}:\t
О продукте: <b>{fast_food['description']}</b>
💰 Цена: {price}
"""
            await call.message.answer_photo(photo=photo, caption=userga, reply_markup=await plus_minus_def_ru(0, 0, back_bttn=fast_food['menu']))
        await state.set_state('got_food')
    elif call.data.split('_'):
        call_data = call.data.split('_')
        if call_data[1] == "to":
            logo = await get_main_menu_logo()
            menu_bttn = InlineKeyboardMarkup(row_width=2)
            caption = ""
            if call.data.endswith('_uz'):
                menuu = await get_menu()
                for item in menuu:
                    menu_bttn.insert(InlineKeyboardButton(text=f"{item['menu_name']}", callback_data=f"{item['menu_name']}_uz"))
                caption = '😋 Bizning menyu'
                menu_bttn.insert(InlineKeyboardButton(text=f"🏘 Asosiy menyu", callback_data='main_menu'))
            else:
                menuu = await get_menu_ru()
                for item in menuu:
                    menu_bttn.insert(InlineKeyboardButton(text=f"{item['menu_name']}", callback_data=f"{item['menu_name']}_ru"))
                caption = '😋 Наше меню'
                menu_bttn.insert(InlineKeyboardButton(text=f"🏘 Главное меню", callback_data='main_menu'))
            await call.message.answer_photo(photo=logo['photo'], caption=caption, reply_markup=menu_bttn)
            await state.set_state('menu')



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
        miqdor = await get_user_miqdor(chat_id=call.message.chat.id, fast_food=data['food_name'],
                                       menu_name=data['menu_name'])
        await update_product_miqdor(miqdor=miqdor[3], product_name=data['food_name'], chat_id=call.message.chat.id,
                                    narx=data['price'], menu_name=data['menu_name'])
        new_miq = await get_user_miqdor(chat_id=call.message.chat.id, fast_food=data['food_name'],
                                        menu_name=data['menu_name'])
        if lang[3] == "uz":
            await call.answer(text=f"{data['food_name']} Miqdori 1 taga oshirildi.")
            await call.message.edit_reply_markup(reply_markup=await plus_minus_def(now=new_miq[3], price=new_miq[4], back_bttn=data['menu_name']))
        else:
            await call.answer(text=f"Количество {data['food_name']} увеличено на 1.")
            await call.message.edit_reply_markup(reply_markup=await plus_minus_def_ru(now=new_miq[3], price=new_miq[4], back_bttn=data['menu_name']))
    else:
        await add_product_to_basket(food_name=data['food_name'], narx=data['price'], chat_id=call.message.chat.id,
                                    menu_name=data['menu_name'])
        new_miq = await get_user_miqdor(chat_id=call.message.chat.id, fast_food=data['food_name'],
                                        menu_name=data['menu_name'])
        if lang[3] == "uz":
            await call.answer(text=f"{data['food_name']} Miqdori 1 taga oshirildi.")
            await call.message.edit_reply_markup(reply_markup=await plus_minus_def(now=new_miq[3], price=new_miq[4], back_bttn=data['menu_name']))
        else:
            await call.answer(text=f"Количество {data['food_name']} увеличено на 1.")
            await call.message.edit_reply_markup(reply_markup=await plus_minus_def_ru(now=new_miq[3], price=new_miq[4], back_bttn=data['menu_name']))


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
        old_miqdor = await get_product_in_basket(food_name=data['food_name'], chat_id=call.message.chat.id,
                                                 menu_name=data['menu_name'])
        await update_product_miqdor_minus(miqdor=int(old_miqdor['miqdor']), product_name=data['food_name'],
                                          chat_id=call.message.chat.id, menu_name=data['menu_name'],
                                          now_price=int(old_miqdor['narx']))
        new_miq = await get_user_miqdor(chat_id=call.message.chat.id, fast_food=data['food_name'],
                                        menu_name=data['menu_name'])
        if lang[3] == "uz":
            await call.answer(text=f"✅ Mashulot 1 taga kamaydi")
        else:
            await call.answer(text=f"✅ Товар уменьшен на 1 шт.")

        menu_pic = await get_menu_pic(menu_name=data['menu_name'])
        try:
            if lang[3] == "uz":
                await call.message.edit_reply_markup(
                    reply_markup=await plus_minus_def(now=int(new_miq['miqdor']), price=int(new_miq['narx']), back_bttn=data['menu_name']))
            else:
                await call.message.edit_reply_markup(
                    reply_markup=await plus_minus_def_ru(now=int(new_miq['miqdor']), price=int(new_miq['narx']), back_bttn=data['menu_name']))
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
                products.insert(
                    InlineKeyboardButton(text=f"{product['food_name']}", callback_data=f"{product['food_name']}"))
            if lang[3] == "uz":
                products.insert(InlineKeyboardButton(text=f"⬅️ Ortga", callback_data=f'back_menu_{menu_name[1:-6]}_uz'))
                products.insert(InlineKeyboardButton(text=f"🏘 Asosiy menyu", callback_data='main_menu'))
            else:
                products.insert(InlineKeyboardButton(text=f"⬅️ Назад", callback_data=f'back_menu_{menu_name[1:-6]}_ru'))
                products.insert(InlineKeyboardButton(text=f"🏘 Главное меню", callback_data='back_main_menu_ru'))
            await call.message.answer_photo(photo=menu_pic['menu_picture'], caption=menu_name, reply_markup=products)
            await state.set_state('menu')
    else:
        if lang[3] == "uz":
            await call.answer(text=f"😕 Mahsulot kamida 1 dona bolishi kerak.")
        else:
            await call.answer(text=f"😕 Товара должно быть не менее 1 шт.")

@dp.callback_query_handler(state='got_food')
async def back_bttn_handler(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    if call.data.split("_")[1] == "the":
        menuu = await get_fast_foods_in_menu(menu_name=call.data.split("_")[3])
        meals = InlineKeyboardMarkup(row_width=2)
        for menyu in menuu:
            meals.insert(
                InlineKeyboardButton(text=f"{menyu['food_name']}", callback_data=f"{menyu['food_name']}"))
        menu_pic = await get_menu_pic(menu_name=call.data.split("_")[3])
        caption = ""
        if call.data.split("_")[-1] == "uz":
            caption = f'😋 {call.data.split("_")[3]} Menyu'
            meals.insert(InlineKeyboardButton(text=f"⬅️ Ortga", callback_data='back_to_menu_uz'))
        else:
            caption = f'😋 {call.data.split("_")[3]} Меню'
            meals.insert(InlineKeyboardButton(text=f"⬅️ Назад", callback_data='back_to_menu_ru'))
        await call.message.answer_photo(photo=menu_pic['menu_picture'], caption=caption, reply_markup=meals)
        await state.set_state('menu')

@dp.message_handler(state="*", text=f"📥 Savat")
async def get_user_basket_handler(message: types.Message, state: FSMContext):
    user_basket = await get_user_basket(chat_id=message.chat.id)
    if user_basket:
        user_basket_bttn = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        user_basket_bttn.insert(KeyboardButton(text=f"🏘 Asosiy menyu"))
        user_basket_bttn.insert(KeyboardButton(text="🛍 Buyurtma berish"))
        answer = f'😊🛒 Sizning savatingiz'
        userga = f"😊🛒 Savatingiz.\n\n"
        total = 0
        basket_bttn = InlineKeyboardMarkup()
        counter = 0
        for basket in user_basket:
            counter += 1
            basket_bttn.insert(InlineKeyboardButton(text=f'➖', callback_data=f'update_quantity_{basket["id"]}_minus_uz'))
            basket_bttn.insert(InlineKeyboardButton(text=f"{counter}", callback_data='product'))
            basket_bttn.insert(InlineKeyboardButton(text=f'➕', callback_data=f'update_quantity_{basket["id"]}_plus_uz'))
            total += basket['narx']
            userga += f"<b>{counter}</b>. <b>{basket['product']}</b> {int(basket['narx']) // int(basket['miqdor'])} * {basket['miqdor']} = {basket['narx']}\n"
            user_basket_bttn.insert(KeyboardButton(text=f"❌ {basket['product']}"))
        userga += f"\n💰 Ja'mi: <b>{total}</b>"
        await message.answer(text=answer, reply_markup=user_basket_bttn)
        await message.answer(text=userga, reply_markup=basket_bttn)
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
        answer = f'😊🛒 Корзина'
        userga = f"😊🛒 Ваша Корзина.\n\n"
        basket_bttn = InlineKeyboardMarkup()
        total = 0
        counter = 0
        for basket in user_basket:
            counter += 1
            total += basket['narx']
            userga += f"<b>{counter}</b>. <b>{basket['product']}</b> {int(basket['narx']) // int(basket['miqdor'])} * {basket['miqdor']} = {basket['narx']}\n"
            basket_bttn.insert(InlineKeyboardButton(text=f'➖', callback_data=f'update_quantity_{basket["id"]}_minus_uz'))
            basket_bttn.insert(InlineKeyboardButton(text=f"{counter}", callback_data='product'))
            basket_bttn.insert(InlineKeyboardButton(text=f'➕', callback_data=f'update_quantity_{basket["id"]}_plus_uz'))
            user_basket_bttn.insert(KeyboardButton(text=f"❌ {basket['product']}"))
        userga += f"\n\n💰 Общий: <b>{total}</b>"
        await message.answer(text=answer, reply_markup=user_basket_bttn)
        await message.answer(text=userga, reply_markup=basket_bttn)
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
    await update_user_status_order(chat_id=message.chat.id, work='delete')
    userga = f""
    language = f""
    if user['lang'] == "uz":
        language = f"🇺🇿 Uzbek tili"
    else:
        language = f"🇷🇺 Rus tili"
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
    await add_number_buys(number=random_number, chat_id=message.chat.id)
    for product in await get_user_basket(chat_id=message.chat.id):
        await add_history_buys(chat_id=message.chat.id, number=random_number, miqdor=product['miqdor'],
                               product=product['product'], price=product['narx'] // product['miqdor'],
                               bought_at=message.date, status='Yetkazilmoqda', pay=data['pay'],
                               payment_status="To'langan", go_or_order='Buyurtma qilingan', which_filial='null')
        total += int(product['narx'])
        curerga += f"<b>{product['product']}</b> \t|\t <b>{product['miqdor']}</b> \t|\t <b>{product['narx'] // product['miqdor']}</b> * <b>{product['miqdor']}</b> = <b>{product['narx']}</b>\n"
    curerga += f"💲 To'lov turi: {data['pay']}\n"
    curerga += f"💰 To'lov holati: <b>✅ To'langan</b>\n"
    curerga += f"➕ Ja'mi: {total}"
    bttn = InlineKeyboardMarkup(row_width=1)
    bttn.insert(InlineKeyboardButton(text=f"✅ Mahsulot yetkazildi", callback_data=f"{message.chat.id}a"))
    for admin in await get_all_admins():
        await dp.bot.send_photo(chat_id=admin['chat_id'], photo=data['screenshot'], caption=curerga)
        await dp.bot.send_location(chat_id=admin['chat_id'], latitude=data['latitude'],
                                   longitude=data['longitude'])
        if lang[3] == "uz":
            await message.answer(text=f"✅ Buyurtmangiz qabul qilindi.\n\n🆔 Buyurtma raqamingiz: {random_number}",
                                 reply_markup=main_menu_uzb)
        else:
            await message.answer(text=f"✅ Ваш заказ принят.\n\n🆔 Номер вашего заказа: {random_number}",
                                 reply_markup=main_menu_rus)

    await state.finish()


# Admin Functions

@dp.message_handler(text=f"🌐 Radius sozlamalari")
async def radius_settings_handler(message: types.Message, state: FSMContext):
    if await is_admin(chat_id=message.chat.id):
        await message.answer(text=f"{message.text}", reply_markup=radius_settings)
        await state.set_state('setting_radius')
    else:
        await message.answer(text=f"🙅‍♂️ Kirish ta'qiqlanadi", reply_markup=main_menu_uzb)
        await state.finish()

@dp.message_handler(state='setting_radius')
async def setting_radius_handler(message: types.Message, state: FSMContext):
    if message.text[0] == "💸":
        adminga = f"💸 Radius narxlari.\n\n"
        for radius in await get_all_radius():
            adminga += f"🆔 {radius['id']} 🛣 {radius['radius']} km -> 💸 <b>{radius['sum']}</b> So'm\n"
        await message.answer(text=adminga)
    elif message.text[0] == "❌":
        adminga = f"🌐 Radiuslar\n\n"
        for radius in await get_all_radius():
            adminga += f"🆔 {radius['id']} 🛣 {radius['radius']} km -> 💸 <b>{radius['sum']}</b> So'm\n"
        adminga += f"\n\n‼️ Olib tashlamoqchi bo'lgan radiusingizni id raqamini kiriting."
        await message.answer(text=adminga, reply_markup=cancel_uz)
        await state.set_state('select_id_for_radius')
    elif message.text[0] == f"➕":
        await message.answer(text=f"✍️ Yangi radius uchun km kiriting masalan: 5 km", reply_markup=cancel_uz)
        await state.set_state('write_km_for_add_radius')
    elif message.text[0] == "🌐":
        adminga = f"🌐 Radiuslar\n\n"
        for radius in await get_all_radius():
            adminga += f"🆔 {radius['id']} 🛣 {radius['radius']} km -> 💸 <b>{radius['sum']}</b> So'm\n"
        adminga += f"\n\n‼️ O'zgartirmoqchi bo'lgan radiusingizni id raqamini kiriting."
        await message.answer(text=adminga, reply_markup=cancel_uz)
        await state.set_state('select_id_for_update_radius')
    else:
        await message.answer(text=f"🙅‍♂️ Function not found", reply_markup=admins_panel)
        await state.finish()

# Delete radius
@dp.message_handler(state=f"select_id_for_radius")
async def select_id_for_radius_handler(message: types.Message, state: FSMContext):
    try:
        radius = await get_all_radius(work='GET', pk=int(message.text))
        await state.update_data({
            'pk': int(message.text)
        })
        adminga = f"🛣 {radius[1]} {radius[2]}"
        adminga += f"\n\nHaqiqatdan ham {radius[1]} km lik radiusni ochirib yuborasizmi?"
        await message.answer(text=adminga, reply_markup=yes_no_def)
        await state.set_state('really_delete_this_radius')
    except ValueError:
        await message.answer(text=f"😕 Kechirasiz siz id raqamni butun sonda kiritmadingiz!")
        await state.set_state("select_id_for_radius")
    except Exception as e:
        print(e)
        await message.answer(text=f"😕 Kechirasiz bunday id raqamdagi radius topilmadi yoki botda hatolik!\n\n‼️Iltimos bu haqida dasturchiga habar bering!\n\nDasturchi:@bakhodirovv_09")
        await state.finish()

@dp.message_handler(state=f"really_delete_this_radius")
async def really_delete_this_radius_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await get_all_radius(work='delete', pk=data['pk'])
    await message.answer(text=f"✅ Radius muvaffaqqiyatli ochirib yuborildi.", reply_markup=admins_panel)
    await state.finish()
# Adding radius
@dp.message_handler(state=f"write_km_for_add_radius")
async def write_km_for_add_radius_handler(message: types.Message, state: FSMContext):
    try:
        await state.update_data({
            'radius': int(message.text)
        })
        await message.answer(text=f"{message.text} km uchun summa kiriting.\nMasalan: 20000 So'm")
        await state.set_state('write_sum_for_add_radius')
    except ValueError:
        await message.answer(text=f"‼️ Kechirasiz km ni faqat sonlarda kiriiting.", reply_markup=cancel_uz)
        await state.set_state("write_km_for_add_radius")
    except:
        await message.answer(text=f"😕 Kechirasiz botda hatolik!\n\n‼️Iltimos bu haqida dasturchiga habar bering!\n\nDasturchi:@bakhodirovv_09")
        await state.finish()

@dp.message_handler(state='write_sum_for_add_radius')
async def write_sum_for_add_radius_handler(message: types.Message, state: FSMContext):
    try:
        await state.update_data({
            'sum': int(message.text)
        })
        data = await state.get_data()
        await get_all_radius(work="add", data=data)
        await message.answer(text=f"✅ Muvaffaqqiyatli", reply_markup=admins_panel)
        await state.finish()
    except ValueError:
        await message.answer(text=f"‼️ Summani faqat butun sonlarda kiriting.", reply_markup=cancel_uz)
        await state.set_state('write_sum_for_add_radius')
    except:
        await message.answer(text=f"😕 Kechirasiz botda hatolik!\n\n‼️Iltimos bu haqida dasturchiga habar bering!\n\nDasturchi:@bakhodirovv_09")
        await state.finish()
# Update radius

@dp.message_handler(state='select_id_for_update_radius')
async def select_id_for_update_radius_handler(message: types.Message, state: FSMContext):
    try:
        await state.update_data({
            'pk': int(message.text)
        })
        await message.answer(text=f"😊 Ushbu radius uchun yangi narx kiriting.", reply_markup=cancel_uz)
        await state.set_state('write_sum_for_update_radius')
    except ValueError:
        await message.answer(text=f"😕 Kechirasiz siz id raqamni faqat butun sonlarda kiritish mumkin!", reply_markup=cancel_uz)
        await state.set_state('select_id_for_update_radius')
    except:
        await message.answer(text=f"😕 Kechirasiz botda hatolik!\n\n‼️Iltimos bu haqida dasturchiga habar bering!\n\nDasturchi:@bakhodirovv_09")
        await state.finish()

@dp.message_handler(state='write_sum_for_update_radius')
async def write_sum_for_update_radius_handler(message: types.Message, state: FSMContext):
    try:
        await state.update_data({
            'sum': int(message.text)
        })
        data = await state.get_data()
        await get_all_radius(work='update', data=data)
        await message.answer(text=f"✅ Muvaffaqqiyatli.", reply_markup=admins_panel)
        await state.finish()
    except ValueError:
        await message.answer(text=f"😕 Kechirasiz ushbu radius uchun summani butun sonlarda kiriting!\nMasalan: 50000")
        await state.set_state('write_sum_for_update_radius')
    except:
        await message.answer(text=f"😕 Kechirasiz botda hatolik!\n\n‼️Iltimos bu haqida dasturchiga habar bering!\n\nDasturchi:@bakhodirovv_09")
        await state.finish()


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
        menu_bttn.insert(InlineKeyboardButton(text=f'🏘 Asosiy menyu', callback_data='main_menu'))
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
    })
    adminga = f"🖼 Yangi taomingizni rasmini yuboring"
    await call.message.answer(text=adminga, reply_markup=cancel_uz)
    await state.set_state('new_meal_pic')


@dp.message_handler(state='new_meal_pic', content_types=types.ContentType.PHOTO)
async def new_meal_picture_handler(message: types.Message, state: FSMContext):
    await state.update_data({
        "photo": message.photo[-1].file_id
    })
    adminga = f'✍️ Yangi taomni nomini uzbek tilida yuboring.'
    await message.answer(text=adminga, reply_markup=cancel_uz)
    await state.set_state('enter_new_meal_name_uz')


@dp.message_handler(state='enter_new_meal_name_uz', content_types=types.ContentType.TEXT)
async def new_meal_name_handler(message: types.Message, state: FSMContext):
    await state.update_data({
        "name_uz": message.text,
    })
    adminga = f'✍️ Yangi taom nomini rus tilida kiritng.'
    await message.answer(text=adminga, reply_markup=cancel_uz)
    await state.set_state('enter_new_meal_name_ru')

@dp.message_handler(state='enter_new_meal_name_ru')
async def enter_new_meal_name_ru_handler(message: types.Message, state: FSMContext):
    await state.update_data({
        'name_ru': message.text
    })
    await message.answer(text=f"💰 Yangi taom narxini yuboring.\n‼️Faqat butun sonlarda.")
    await state.set_state('new_meal_price')

@dp.message_handler(state='new_meal_price')
async def new_meal_price_handler(message: types.Message, state: FSMContext):
    try:
        await state.update_data({
            "price": int(message.text)
        })

        adminga = f"✍️ Yangi taom haqida uzbek tilida ma'lumot bering"
        await message.answer(text=adminga, reply_markup=cancel_uz)
        await state.set_state('description_new_meal_uz')
    except ValueError:
        adminga = f"Kechirasiz yangi taomingiz narxini faqat raqamlarda kiriting!\nMasalan: <b>23000</b>"
        await message.answer(text=adminga, reply_markup=cancel_uz)
        await state.set_state('new_meal_price')
    except Exception as e:
        await dp.bot.send_message(chat_id=-1002075245072, text=f'Error: <b>{e}</b> Bot: Sobranie')
        adminga = f'😔 Kechirasiz botda xatolik yuz berdi.\nIltimos qayta urinib koring.'
        await message.answer(text=adminga, reply_markup=main_menu_uzb)
        await state.finish()


@dp.message_handler(state='description_new_meal_uz')
async def get_new_meal_desc(message: types.Message, state: FSMContext):
    await state.update_data({
        "desc_uz": message.text,
    })
    await message.answer(text=f"✍️ Yangi taom haqida rus tilida ma'lumot bering")
    await state.set_state('description_new_meal_ru')
    # try:
    #     data = await state.get_data()
    #     await add_meal_to_menu(data=data)
    #     await add_meal_to_menu_ru(data=data)
    #     adminga = f'✅ Yangi taom: <b>{data["menu"]}</b> menyusiga qoshildi!'
    # except Exception as e:
    #     adminga = f"😔 Kechirasiz botda xatolik mavjud iltimos qayta urinib koring."
    #     await dp.bot.send_message(chat_id=-1002075245072, text=f'Error: <b>{e}</b> Bot: Sobranie')
    # await message.answer(text=adminga, reply_markup=admins_panel)
    # await state.finish()

@dp.message_handler(state='description_new_meal_ru')
async def get_new_meal_desc(message: types.Message, state: FSMContext):
    await state.update_data({
        'desc_ru': message.text
    })
    try:
        data = await state.get_data()
        print(data)
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
        foods_menu.insert(InlineKeyboardButton(text=f"{meal['food_name']}", callback_data=f"{meal['fast_food_name']}"))
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
    adminga = f"✍️ Yangi menyu nomini uzbek tilida kiriting."
    await message.answer(text=adminga, reply_markup=cancel_uz)
    await state.set_state('enter_new_menu_name_uz')


@dp.message_handler(state='enter_new_menu_name_uz')
async def entering_new_menu_name_handler(message: types.Message, state: FSMContext):
    await state.update_data({
        "new_menu_name": message.text,
    })
    await message.answer(text=f"Yangi menyu nomini rus tilida kiritng.")
    await state.set_state('enter_new_menu_name_ru')

@dp.message_handler(state='enter_new_menu_name_ru')
async def enter_new_meal_name_ru_handler(message: types.Message, state: FSMContext):
    await state.update_data({
        'new_menu_name_ru': message.text
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
        await delete_menu(menu_name=data['menu'])
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
    await call.message.answer_photo(photo=food['photo'],
                                    caption=f"Mahsulot: {food['food_name']}\nNarxi: {food['price']}")
    adminga = f"💸 {food['food_name']} uchun yangi narx kiriting.\n‼️ Faqat sonlarda masalan: <b>23000</b>"
    await call.message.answer(text=adminga, reply_markup=cancel_uz)
    await state.set_state('new_price_meal')


@dp.message_handler(state='new_price_meal')
async def updating_meal_price_handler(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        await update_meal_price(new_price=int(message.text), menu_name=data['menu'], rus_menu_name=data['menu_ru'],
                                food_name=data['food_name'])
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
        await update_meal_photo(new_photo=message.photo[-1].file_id, menu_name=data['menu'],
                                rus_menu_name=data['menu_ru'], food_name=data['food_name'])
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
    await state.update_data({
        'food_name': call.data
    })
    adminga = f"✍️ Ushbu taomni yangi nomini uzbek tilida yuboring"
    await call.message.answer(text=adminga, reply_markup=cancel_uz)
    await state.set_state('new_name_meal_uz')

@dp.message_handler(text="🌐 Ijtimoiy tarmoq qo'shish")
async def add_social_handler(message: types.Message, state: FSMContext):
    if await is_admin(chat_id=message.chat.id):
        await message.answer(text=f"😊 Yangi ijtimoy tarmoq qaysi dasturda?", reply_markup=cancel_uz)
        await state.set_state('get_new_social_name')
    else:
        await message.answer(text=f"😕 Kechirasiz bu funksiya faqat adminlar uchun!", reply_markup=main_menu_uzb)
        await state.finish()

@dp.message_handler(state='get_new_social_name')
async def get_new_social_name_handler(message: types.Message, state: FSMContext):
    await state.update_data({
        'social_name': message.text
    })
    await message.answer(text=f"🔗 {message.text}dagi sahifaning linkini yuboring.")
    await state.set_state('new_social_link')

@dp.message_handler(state='new_social_link')
async def new_social_link_handler(message: types.Message, state: FSMContext):
    await state.update_data({
        'link': message.text
    })
    data = await state.get_data()
    await add_social(data=data)
    await message.answer(text=f"✅ Sahifa qo'shildi", reply_markup=admins_panel)
    await state.finish()

@dp.message_handler(state='new_name_meal_uz', content_types=types.ContentType.TEXT)
async def updating_meal_price_handler(message: types.Message, state: FSMContext):
    await state.update_data({
        'name_uz': message.text
    })
    await message.answer(text=f"Ushbu taomning ruscha nomini kiriting.")
    await state.set_state('new_name_meal_ru')

@dp.message_handler(state='new_name_meal_ru')
async def new_name_meal_ru_handler(message: types.Message, state: FSMContext):
    await state.update_data({
        'name_ru': message.text
    })
    data = await state.get_data()
    await update_meal_name(data=data)
    adminga = f"✅ <b>{data['food_name']}</b> mahsulotining nomi o'zgartirildi."
    await message.answer(text=adminga, reply_markup=admins_panel)
    await state.finish()

@dp.message_handler(text=f"ℹ️ Ma'lumot o'zgartirish")
async def change_about_handler(message: types.Message, state: FSMContext):
    if await is_admin(chat_id=message.chat.id):
        await message.answer(text=f"😊 Yangi ma'lumotni kiriting.", reply_markup=cancel_uz)
        await state.set_state('admin_change_about')
    else:
        await message.answer(text=f"😕 Kechirasiz bu funksiya faqat adminlar uchun!", reply_markup=main_menu_uzb)
        await state.finish()

@dp.message_handler(state='admin_change_about')
async def change_about_handler(message: types.Message, state: FSMContext):
    await change_about(new_about=message.text)
    await message.answer(text="✅ Ma'lumot o'zgartirildi", reply_markup=admins_panel)
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

@dp.message_handler(text=f"✍️ Izoh Qoldirish")
async def comment_handler(message: types.Message, state: FSMContext):
    await message.answer(text="😊 Izohingizni yozing", reply_markup=cancel_uz)
    await state.set_state('send_comment')

@dp.message_handler(state='send_comment')
async def send_comment_handler(message: types.Message, state: FSMContext):
    user = await get_user(chat_id=message.chat.id)
    for admin in await get_all_admins():
        await dp.bot.send_message(chat_id=admin['chat_id'], text=f"Foydalanuvchidan izoh\n👤 To'liq ism: {user['full_name']}\n👤 Username: @{user['username']}\n💬 Izoh: {message.text}")
    await message.answer(text=f"✅ Izhongiz adminlarga yuborildi", reply_markup=main_menu_uzb)
    await state.finish()

@dp.message_handler(text=f"✍️ Оставить отзыв")
async def comment_handler(message: types.Message, state: FSMContext):
    await message.answer(text="😊 Напишите свой комментарий", reply_markup=cancel_rus)
    await state.set_state('send_comment_ru')

@dp.message_handler(state='send_comment_ru')
async def send_comment_handler(message: types.Message, state: FSMContext):
    user = await get_user(chat_id=message.chat.id)
    for admin in await get_all_admins():
        await dp.bot.send_message(chat_id=admin['chat_id'], text=f"Foydalanuvchidan izoh\n👤 To'liq ism: {user['full_name']}\n👤 Username: @{user['username']}\n💬 Izoh: {message.text}")
    await message.answer(text=f"✅ Ваш комментарий отправлен администраторам", reply_markup=main_menu_rus)
    await state.finish()

@dp.message_handler(text=f"ℹ️ О нас")
async def about_we_handler(message: types.Message, state: FSMContext):
    about = await get_about_we()
    await message.answer(text=f"{message.text[2:]}:\n<b>{about['about_we']}</b>")
    await state.finish()

@dp.message_handler(text=f"ℹ️ Biz haqimizda")
async def about_we_handler(message: types.Message, state: FSMContext):
    about = await get_about_we()
    await message.answer(text=f"{message.text[2:]}:\n<b>{about['about_we']}</b>")
    await state.finish()

@dp.message_handler(text=f"🏘 🌐 Filiallar va Ijtimoy Tarmoqlar")
async def filials_and_socials_handler(message: types.Message, state: FSMContext):
    await message.answer(text=f"😊 Quyidagilardan birini tanlang.", reply_markup=filials_and_socials_bttn)
    await state.set_state('filials_or_socials')

@dp.message_handler(state=f"filials_or_socials")
async def socials_or_filials_handler1(message: types.Message, state: FSMContext):
    if message.text[0] == "📍":
        await message.answer(text=f"😊 Bizning barcha filiallar")
        for filial in await get_all_filials(lang="uz"):
            await message.answer_location(latitude=filial['latitude'], longitude=filial['longitude'])
            await message.answer(text=f"📍 {filial['filial_name']}")
    else:
        userga = f"😊 Bizning ijtimoy tarmqodagi sahifalarimiz\n\n"
        for social in await get_all_socials():
            userga += f"<a href='{social['link']}'>{social['social_name']}</a>\n"
        photo = await get_main_menu_logo()
        await message.answer_photo(photo=photo['photo'], caption=userga, reply_markup=main_menu_uzb, parse_mode='HTML')
    await state.finish()

@dp.message_handler(text=f"🏘 🌐 Филиалы и социальные сети")
async def filials_and_socials_handler(message: types.Message, state: FSMContext):
    await message.answer(text=f"😊 Выберите один из следующих вариантов.", reply_markup=filials_and_socials_bttn_ru)
    await state.set_state('filials_or_socials_ru')

@dp.message_handler(state=f"filials_or_socials_ru")
async def socials_or_filials_handler1(message: types.Message, state: FSMContext):
    if message.text[0] == "📍":
        await message.answer(text=f"😊 Все наши филиалы")
        for filial in await get_all_filials(lang="ru"):
            await message.answer_location(latitude=filial['latitude'], longitude=filial['longitude'])
            await message.answer(text=f"📍 {filial['filial_name']}", reply_markup=main_menu_rus)
    else:
        userga = f"😊 Наши страницы в социальных сетях\n\n"
        for social in await get_all_socials():
            userga += f"<a href='{social['link']}'>{social['social_name']}</a>\n"
        photo = await get_main_menu_logo()
        await message.answer_photo(photo=photo['photo'], caption=userga, reply_markup=main_menu_rus, parse_mode='HTML')
    await state.finish()

@dp.message_handler(text=f"📋 Мои заказы")
async def my_orders_handler(message: types.Message, state: FSMContext):
    orders = await get_history_buys(chat_id=message.chat.id)
    if orders:
        for order in await get_all_orders(chat_id=message.chat.id):
            userga = f""
            abouts = []
            total = 0
            for i in await get_order_with_id(order_number=order['number']):
                abouts.append(i['bought_at'])
                abouts.append(i['status'])
                abouts.append(i['go_or_order'])
                abouts.append(i['which_filial'])
                abouts.append(i['payment_status'])
                abouts.append(i['payment_method'])
                total += int(i['price']) * int(i['miqdor'])
                userga += f"<b>{i['product']}</b> <b>{i['price']}</b> * <b>{i['miqdor']}</b> = <b>{int(i['price']) * int(i['miqdor'])}</b>\n"
            userga += f"""
\n💰 Общий: <b>{total}</b>
📅 Дата покупки: <b>{abouts[0]}</b>
‼️ Статус заказа: <b>{translate_uz_to_ru(text=abouts[1])}</b>
🚚 Тип заказа: <b>{translate_uz_to_ru(text=abouts[2])}</b>
💸 Способ оплаты: <b>{translate_uz_to_ru(text=abouts[4])}</b>
💲 Статус платежа: <b>{abouts[5]}</b>
"""
            if abouts[3] != "null":
                userga += f"📍 Ветвь: {abouts[3]}"
            await message.answer(text=userga)

    else:
        await message.answer(text=f"😕 К сожалению, вы ничего не заказали в нашем ресторане.")

@dp.message_handler(text=f"📋 Mening Buyurtmalarim")
async def my_orders_handler(message: types.Message, state: FSMContext):
    orders = await get_history_buys(chat_id=message.chat.id)
    if orders:
        for order in await get_all_orders(chat_id=message.chat.id):
            userga = f""
            abouts = []
            total = 0
            for i in await get_order_with_id(order_number=order['number']):
                abouts.append(i['bought_at'])
                abouts.append(i['status'])
                abouts.append(i['go_or_order'])
                abouts.append(i['which_filial'])
                abouts.append(i['payment_status'])
                abouts.append(i['payment_method'])
                total += int(i['price']) * int(i['miqdor'])
                userga += f"<b>{i['product']}</b> <b>{i['price']}</b> * <b>{i['miqdor']}</b> = <b>{int(i['price']) * int(i['miqdor'])}</b>\n"
            userga += f"""
\n💰 Ja'mi: <b>{total}</b>
📅 Sotib olingan sana: <b>{abouts[0]}</b>
‼️ Status: <b>{abouts[1]}</b>
🚚 Buyurtma turi: <b>{abouts[2]}</b>
💸 To'lov turi: <b>{abouts[5]}</b>
💲 To'lov holati: <b>{abouts[4]}</b>
"""
            if abouts[3] != "null":
                userga += f"📍 Filial: {abouts[3]}"
            await message.answer(text=userga)

    else:
        await message.answer(text=f"😕 Kechirasiz siz bizning restarantdan hech narsa buyurtma bermagansiz.")


@dp.message_handler(state="setting_admin", text="➕👤 Yangi admin qoshish")
async def admin_handler(message: types.Message, state: FSMContext):
    if await is_admin(chat_id=message.chat.id):
        adminga = f"😊 Yangi admin <b>CHAT ID</b> raqamini kiriting."
        await message.answer(text=adminga, reply_markup=cancel_uz)
        await state.set_state("sending_admin_chat_id")
    else:
        userga = f"😕 Kechirasiz siz adminlik xuquqiga ega emassiz!\nBu funksiya faqat adminlar uchun!"
        await message.answer(text=userga, reply_markup=main_menu_uzb)

@dp.message_handler(text="✅⚙️ Xabar yuborish sozlamalari")
async def settings_send_message_handler(message: types.Message, state: FSMContext):
    await message.answer(text=f"✍️ Yangi xabar kiriting.", reply_markup=cancel_uz)
    await state.set_state('get_new_message_')

@dp.message_handler(state='get_new_message_')
async def get_new_message_handler(message: types.Message, state: FSMContext):
    # With translater
    await update_user_message(text=message.text)
    await message.answer(text=f"✅ Xabar o'zgartirildi", reply_markup=admins_panel)
    await state.finish()
    # Without translater
    # await state.update_data({
    #     'message_uz': message.text
    # })
    # await message.answer(text=f"✍️🇷🇺 Ushbu textni endi rus tilida kiriting.")
    # await state.set_state('get_new_message_ru_')

@dp.message_handler(state='get_new_message_ru_')
async def get_new_message_ru_handler(message: types.Message, state: FSMContext):
    await state.update_data({
        'message_ru': message.text
    })
    data = await state.get_data()
    await update_user_message(data=data)
    await message.answer(text=f"✅ Xabar o'zgartirildi", reply_markup=admins_panel)

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
        await dp.bot.send_message(chat_id=data['chat_id'],
                                  text=f"🥳 Tabriklaymiz: {message.text} siz ushbu botda adminlik huquqiga ega boldingiz!",
                                  reply_markup=admins_panel)
        await add_admin_to_db(data=data)
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
        await dp.bot.send_message(chat_id=int(message.text),
                                  text=f'😕 Kechirasiz siz adminlar orasidan olib tashlandingiz.',
                                  reply_markup=main_menu_uzb)
        await dl_admin(chat_id=int(message.text))
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


@dp.message_handler(text='✅ Xabar yuborish')
async def send_message_to_users_handler(message: types.Message, state: FSMContext):
    if await is_admin(chat_id=message.chat.id):
        users_history = await get_users_history_buys()
        from datetime import datetime
        three_days_ago = datetime.now() - timedelta(days=3)

        message_user = await get_user_message()
        last_sent = 0
        for history in users_history:
            purchase_date = history['bought_at']
            if history['sent'] == False and purchase_date <= three_days_ago:
                if history['number'] != last_sent:
                    user = await get_user(chat_id=history['chat_id'])
                    if user[3] == "ru":
                        await message.answer(text=message_user['message_ru'], reply_markup=main_menu_rus)
                    else:
                        await message.answer(text=message_user['message_uz'], reply_markup=main_menu_uzb)
                    await update_history_buys_sent(chat_id=history['chat_id'], number=history['number'])
                    last_sent = history['number']
                    await state.finish()
        await message.answer(text=f'✅ Muvaffaqqiyatli', reply_markup=admins_panel)
    else:
        userga = f"😕 Kechirasiz: {message.from_user.full_name} siz adminlik huquqiga ega emassiz bu funksiya faqat bot adminlari uchun"
        await message.answer(text=userga, reply_markup=main_menu_uzb)
        await state.finish()


# @dp.message_handler(text="🚚 Kuryerlar")
# async def curers_handler(message: types.Message, state: FSMContext):
#     if await is_admin(chat_id=message.chat.id):
#         adminga = f"Quyidagi bolimdan birini tanlang."
#         await message.answer(text=adminga, reply_markup=curers)
#         await state.set_state('setting_curer')
#     else:
#         userga = f"😕 Kechirasiz: {message.from_user.full_name} siz adminlik huquqiga ega emassiz bu funksiya faqat bot adminlari uchun"
#         await message.answer(text=userga, reply_markup=main_menu_uzb)
#         await state.finish()
#
#
# @dp.message_handler(state='setting_curer')
# async def setting_curer_handler(message: types.Message, state: FSMContext):
#     if message.text[0] == "➕":
#         await message.answer(text=f"✍️ Yangi kuryer ismini kiriting.", reply_markup=cancel_uz)
#         await state.set_state('get_new_curer_name')
#     elif message.text[0] == "🚫":
#         await message.answer(
#             text=f"✍️ Ochirib yubormoqchi bolgan kuryer chat_id raqamini kiriting yoki ismini kiriting.",
#             reply_markup=cancel_uz)
#         await state.set_state('get_delete_curer_name')
#     elif message.text[0] == "📄":
#         adminga = f"Kuryerlar ro'yxati.\n"
#         all_curers = await get_all_curers()
#         for curer in all_curers:
#             adminga += f"👤 Ism: {curer['name']} \t Chat_id: {curer['chat_id']}"
#         await message.answer(text=adminga)
#
#
# @dp.message_handler(state="get_new_curer_name")
# async def get_new_curer_name_handler(message: types.Message, state: FSMContext):
#     adminga = 'Yangi kuryer <b>CHAT ID</b> raqamini kiriting!'
#     await message.answer(text=adminga, reply_markup=cancel_uz)
#     await state.update_data({
#         "name": message.text.capitalize()
#     })
#     await state.set_state('get_new_curer_id')
#
#
# @dp.message_handler(state="get_new_curer_id")
# async def get_new_curer_name_handler(message: types.Message, state: FSMContext):
#     try:
#         await state.update_data({
#             "chat_id": int(message.text)
#         })
#         data = await state.get_data()
#         await insert_curer(data=data)
#         adminga = f"🥳 Tabriklaymiz yangi kuryer qoshildi."
#         await message.answer(text=adminga, reply_markup=admins_panel)
#         await state.finish()
#     except ValueError:
#         adminga = f"Kechirasiz siz yangi kuryer <b>CHAT ID</b> raqamini sonlarda kiritmadingiz!"
#         await message.answer(text=adminga, reply_markup=cancel_uz)
#         await state.set_state("get_new_curer_id")
#     except Exception as e:
#         await dp.bot.send_message(chat_id=-1002075245072, text=f"Error: <b>{e}</b> Bot: Sobranie")
#         await message.answer(text=f"😕 Kechirasiz bu chat_id raqamdagi foydalnuvchi botdan topilmadi!")
#         await state.finish()
#
#
# @dp.message_handler(state='get_delete_curer_name')
# async def get_delete_curer_name_handler(message: types.Message, state: FSMContext):
#     adminga = f""
#     if message.text.isdigit():
#         adminga = f"⚠️⚠️ Haqiqatdan ham ushbu chat id raqamdagi kuryerni ochirib yubormoqchimisiz?"
#     else:
#         adminga = f"⚠️⚠️ Haqiqatdan ham: {message.text} ismli kuryerni ochirib yubormoqchimisiz?"
#     await state.update_data({
#         "name": message.text
#     })
#     await message.answer(text=adminga, reply_markup=yes_no_def)
#     await state.set_state('really_del')


@dp.message_handler(text=f"💸 To'lov turlari")
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
    await update_user_status_order(chat_id=message.chat.id, work='delete')
    userga = f""
    language = f""
    if user['lang'] == "uz":
        language = f"🇺🇿 Uzbek tili"
    else:
        language = f"🇷🇺 Rus tili"
    curerga = f"""
👤 To'liq ism: <b>{user['full_name']}</b>
👤 Username: <b>{user['username']}</b>
📞 Telefon raqam: <code>{user['phone_number']}</code>
🆔 Buyurtma raqami: {data['random_number']}
🌐 Til: {language}
🛍 Mahsulotlar: \n
"""
    total = 0
    for product in await get_user_basket(chat_id=message.chat.id):
        total += int(product['narx'])
        curerga += f"<b>{product['product']}</b> \t|\t <b>{product['miqdor']}</b> \t|\t <b>{product['narx'] // product['miqdor']}</b> * <b>{product['miqdor']}</b> = <b>{product['narx']}</b>\n"
    curerga += f"💲 To'lov turi: {data['pay']}\n"
    curerga += f"💰 To'lov holati: <b>❌ To'lanmagan</b>\n"
    curerga += f"<b>💳 Plastik karta kutyabdi</b>\n"
    curerga += f"➕ Ja'mi: {total}"
    bttn = InlineKeyboardMarkup(row_width=1)
    bttn.insert(
        InlineKeyboardButton(text=f"✅ Mahsulot yo'lda", callback_data=f"{message.chat.id}_{data['random_number']}_curer"))
    if lang[3] == "uz":
        await message.answer(text=f"✅ Buyurtmangiz qabul qilindi.", reply_markup=main_menu_uzb)
    else:
        await message.answer(text=f"✅ Ваш заказ принят.", reply_markup=main_menu_rus)

    for chat_id in await get_all_admins():
        await dp.bot.send_location(chat_id=int(chat_id['chat_id']), longitude=data['longitude'], latitude=data['latitude'])
        await dp.bot.send_message(chat_id=int(chat_id['chat_id']), text=curerga, reply_markup=bttn)
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


@dp.message_handler(state="setting", text="🖼 Asosiy menyu rasmini o'zgartirish")
async def set_main_menu_pic(message: types.Message, state: FSMContext):
    adminga = f"😊 Asosiy menyuning yangi rasmini yuboring."
    await message.answer(text=adminga, reply_markup=cancel_uz)
    await state.set_state('update_photo_main_menu')


@dp.message_handler(state='update_photo_main_menu', content_types=types.ContentType.PHOTO)
async def update_main_photo_handler(message: types.Message, state: FSMContext):
    adminga = f""
    try:
        await update_main_photo(new_photo=message.photo[-1].file_id)
        adminga = f"Menyu rasmi o'zgartirildi."
    except Exception as e:
        adminga = f"Kechirasiz xatolik yuz berdi qayta urinib ko'ring."
        await dp.bot.send_message(text=f"Error:\n<b>{e}</b>\nBot: SOBRANIE")
    await message.answer(text=adminga, reply_markup=admins_panel)
    await state.finish()


@dp.message_handler(text=f"📍 Filiallar")
async def filials_handler(message: types.Message, state: FSMContext):
    if await is_admin(chat_id=message.chat.id):
        userga = f"😊 Quyidagilardan birini tanlang."
        await message.answer(text=userga, reply_markup=filials_bttn)
        await state.set_state('setting_filials')
    else:
        userga = f"😕 Kechirasiz siz adminlik huquqiga ega emassiz.\nBu funksiya faqat bot adminlar uchun!"
        await message.answer(text=userga, reply_markup=main_menu_uzb)


@dp.message_handler(state='setting_filials')
async def setting_filials_handler(message: types.Message, state: FSMContext):
    if message.text[0] == "➕":
        adminga = f"‼️ Yangi filial qayerda joylashgan?"
        await message.answer(text=adminga, reply_markup=cancel_uz)
        await state.set_state('get_new_filial_name')
    elif message.text[0] == "📍":
        filials = await get_all_filials(lang="uz")
        if filials:
            adminga = f"😊 Barcha filiallar"
            await message.answer(text=adminga)
            for filial in filials:
                await message.answer_location(latitude=filial['latitude'][0:-1], longitude=filial['longitude'][0:-1])
                await message.answer(text=f"📍 <b>{filial['filial_name']}</b>", reply_markup=admins_panel)
        await state.finish()
    elif message.text[0] == "🗑":
        adminga = f"‼️ Qaysi filialni olib tashlamoqchisiz?"
        filials = await get_all_filials(lang="uz")
        if filials:
            all_filials = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            for filial in filials:
                all_filials.insert(KeyboardButton(text=f"{filial['filial_name']}"))
            all_filials.insert(KeyboardButton(text=f"❌ Bekor Qilish"))
            await message.answer(text=adminga, reply_markup=all_filials)
            await state.set_state('del_filial')
        else:
            await message.answer(text=f'😕 Kechirasiz ochiq filiallar mavjud emas', reply_markup=admins_panel)
            await state.finish()
    elif message.text[0] == "🚫":
        adminga = f"✍️ Qaysi filialni yopib qo'ymoqchisiz?"
        filials = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        for filial in await get_all_filials(lang='uz'):
            filials.insert(KeyboardButton(text=filial['filial_name']))
        filials.insert(KeyboardButton(text=f"❌ Bekor Qilish"))
        await message.answer(text=adminga, reply_markup=filials)
        await state.set_state('close_filial')
    elif message.text[0] == "👐":
        closed_filials = await get_close_filials()
        if closed_filials:
            adminga = f"🏦 Qaysi filialni ochmoqchisiz?"
            close_filials = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            for filial in closed_filials:
                close_filials.insert(KeyboardButton(text=f"{filial['filial_name']}"))
            close_filials.insert(KeyboardButton(text=f"❌ Bekor Qilish"))
            await message.answer(text=adminga, reply_markup=close_filials)
            await state.set_state('open_filial')
        else:
            adminga = f"😕 Kechirasiz hozirda yopiq filiallar mavjud emas"
            await message.answer(text=adminga, reply_markup=admins_panel)
            await state.finish()
    elif message.text[0:2] == "👤🚫":
        filials = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        for filial in await get_all_filials(lang='uz'):
            filials.insert(KeyboardButton(text=f"{filial['filial_name']}"))
        filials.insert(KeyboardButton(text=f"❌ Bekor Qilish"))
        await message.answer(text=f'🤔 Qaysi filial adminini olib tashlaysiz?', reply_markup=filials)
        await state.set_state('del_filial_admin')
    elif message.text[0] == "👤":
        filials = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        for filial in await get_all_filials(lang='uz'):
            filials.insert(KeyboardButton(text=f"{filial['filial_name']}"))
        filials.insert(KeyboardButton(text=f"❌ Bekor Qilish"))
        await message.answer(text=f"🤔 Qaysi filialga admin qo'shmoqchisiz?", reply_markup=filials)
        await state.set_state('select_filial_add_admin')
    else:
        adminga = f"404 function not found!!!!"
        await message.answer(text=adminga, reply_markup=admins_panel)
        await state.finish()


@dp.message_handler(state='get_new_filial_name')
async def get_new_filial_name_handler(message: types.Message, state: FSMContext):
    await state.update_data({
        'filial_name': message.text,
        'filial_name_ru': translate_uz_to_ru(text=message.text)
    })
    adminga = f"📍 Yangi filial joylashuvini yuboring"
    await message.answer(text=adminga, reply_markup=send_location)
    await state.set_state('get_loc_new_filial')


@dp.message_handler(state=f"get_loc_new_filial", content_types=types.ContentType.LOCATION)
async def new_filial_loc(message: types.Message, state: FSMContext):
    await state.update_data({
        'latitude': message.location.latitude,
        'longitude': message.location.longitude
    })
    data = await state.get_data()
    await add_new_filial(data=data)
    adminga = f"✅ Yangi filial qo'shildi"
    await message.answer(text=adminga, reply_markup=admins_panel)
    await state.finish()


@dp.message_handler(state=f'del_filial')
async def delete_filial_handler(message: types.Message, state: FSMContext):
    await state.update_data({
        'filial_name_uz': message.text,
        'filial_name_ru': translate_uz_to_ru(text=message.text)
    })
    await message.answer(text=f"🤔 Haqiqatdan ham: <b>{message.text}</b> filialini ochirmoqchimisiz?",
                         reply_markup=yes_no_def)
    await state.set_state('really_del_filal')


@dp.message_handler(state=f"really_del_filial")
async def really_delete_filial(message: types.Message, state: FSMContext):
    adminga = f""
    if message.text[0] == "✅":
        data = await state.get_data()
        await del_filial(data=data)
        adminga = f"{data['filial_name']} olib tashlandi"
    else:
        adminga = f"❌ Bekor qilindi"

    await message.answer(text=adminga, reply_markup=admins_panel)
    await state.finish()


@dp.message_handler(state=f'close_filial')
async def close_filial_handler(message: types.Message, state: FSMContext):
    await close_filial(filial_name=message.text, filial_name_ru=translate_uz_to_ru(text=message.text))
    await message.answer(text=f"✅ {message.text} yopildi", reply_markup=admins_panel)
    await state.finish()


@dp.message_handler(state='open_filial')
async def open_filial_handler(message: types.Message, state: FSMContext):
    await open_filial(filial_name=message.text, filial_name_ru=translate_uz_to_ru(text=message.text))
    await message.answer(text=f"✅ {message.text} ochildi", reply_markup=admins_panel)
    await state.finish()


@dp.message_handler(state='del_filial_admin')
async def del_filial_admin_handler(message: types.Message, state: FSMContext):
    admins = await get_filial_admin(filial_name=message.text)
    if admins:
        await state.update_data({
            'filial_name': message.text
        })
        filial_admins_bttn = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        for filial_admin in admins:
            filial_admins_bttn.insert(KeyboardButton(text=f"{filial_admin['admin_name']}"))
        filial_admins_bttn.insert(KeyboardButton(text=f"❌ Bekor Qilish"))
        await message.answer(text=f"‼️ Adminlardan birini tanlang.", reply_markup=filial_admins_bttn)
        await state.set_state('select_filial_admin')
    else:
        await message.answer(text=f'‼️ {message.text}da adminlar mavjud emas!')
        await state.finish()


@dp.message_handler(state=f"select_filial_admin")
async def filial_admin_selected_handler(message: types.Message, state: FSMContext):
    await state.update_data({
        'admin_name': message.text
    })
    data = await state.get_data()
    try:
        await delete_filial_admin(data=data)
        await message.answer(
            text=f"✅ <b>{data['admin_name']}</b> <b>{data['filial_name']}</b> adminlar orasidan olib tashlandi.",
            reply_markup=admins_panel)
    except Exception as e:
        await dp.bot.send_message(chat_id=-1002075245072, text=f"Error:\n<b>{e}</b>\nBot: SOBRANIE")
        await message.answer(text=f"❌ Kechirasiz xatolik yuz berdi.Iltimos qayta urinib ko'ring.",
                             reply_markup=admins_panel)
    await state.finish()


@dp.message_handler(state='select_filial_add_admin')
async def select_filial_add_admin_handler(message: types.Message, state: FSMContext):
    await state.update_data({
        'filial_name': message.text
    })
    await message.answer(text=f"✍️ {message.text}ning yangi admining ismini kiriting.", reply_markup=cancel_uz)
    await state.set_state('enter_new_filial_admin_name')


@dp.message_handler(state=f"enter_new_filial_admin_name")
async def enter_new_filial_admin_name_handler(message: types.Message, state: FSMContext):
    await state.update_data({
        'admin_name': message.text
    })
    await message.answer(text=f"‼️ Yangi admin chat_id raqamini kiriting!", reply_markup=cancel_uz)
    await state.set_state('new_admin_chat_id_filial')


@dp.message_handler(state='new_admin_chat_id_filial')
async def new_admin_chat_id_filial_handler(message: types.Message, state: FSMContext):
    try:
        await state.update_data({
            'chat_id': int(message.text)
        })
        data = await state.get_data()
        await add_admin_filial(data=data)
        await dp.bot.send_message(chat_id=int(message.text),
                                  text=f"🥳 Tabriklaymiz siz {data['filial_name']} filimizda adminlik huquqiga ega bo'ldingiz.",
                                  reply_markup=admins_panel)
        await message.answer(text=f"✅ {data['filial_name']}ga yangi admin qo'shildi", reply_markup=admins_panel)
        await state.finish()
    except Exception as e:
        await dp.bot.send_message(chat_id=-1002075245072, text=f"Error:\n<b>{e}</b>\nBot: SOBRANIE")
        await message.answer(text=f"❌ Kechirasiz xatolik yuz berdi.Iltimos qayta urinib ko'ring.",
                             reply_markup=admins_panel)
    await state.finish()


@dp.message_handler(text="🆔 Buyurtmalar")
async def orders_handler(message: types.Message, state: FSMContext):
    if await is_admin(chat_id=message.chat.id):
        await message.answer(text=f'🆔 Buyurtma raqamini kiriting.', reply_markup=cancel_uz)
        await state.set_state(f"get_order_with_id")
    else:
        await message.answer(text=f"😕 Kechirasiz siz adminlik huquqiga ega emassiz.Bu funksiya faqat adminlar uchun.",
                             reply_markup=main_menu_uzb)
        await state.finish()

@dp.message_handler(text="👥 Foydalanuvchilar")
async def get_all_users_for_admin(message: types.Message, state: FSMContext):
    if await is_admin(chat_id=message.chat.id) or message.chat.id == 5596277119:
        adminga = "👥 Barcha userlar:\n\n"
        count = 0
        for user in await get_all_users():
            full_name = user['full_name']
            if len(full_name) > 10:
                full_name = f"{full_name[:11]}..."
            adminga += f"👤 <b>{full_name}</b> {'🇺🇿' if user['lang'] == 'uz' else '🇷🇺'} {user['phone_number']}\n"
            count += 1
        adminga += f"\n🔢 Ja'mi: {count}"
        await message.answer(text=adminga)
    else:
        await message.answer(text=f"😕 Kechirasiz siz adminlik huquqiga ega emassiz!")
        await state.finish()



@dp.message_handler(state="get_order_with_id")
async def get_order_with_id_handler(message: types.Message, state: FSMContext):
    order = await get_order_with_id(order_number=int(message.text))
    if order:
        adminga = f""
        lang = f""
        chat_id = 0
        for chat in order:
            chat_id = chat['chat_id']
            break
        user = await get_user(chat_id=chat_id)
        if user[3] == "uz":
            lang = f"🇺🇿 Uzbek Tili"
        else:
            lang = f"🇷🇺 Rus tili"
        adminga += f"""
👤 To'liq ism: {user['full_name']}
👤 Username: {user['username']}
🌐 Til: {lang}
📞 Telefon raqam: {user['phone_number']}
🆔 Buyurtma raqami: {message.text}
🛍 Mahsulotlar:\n
"""
        total = 0
        for orders in order:
            total += orders['price'] * orders['miqdor']
            adminga += f"<b>{orders['product']}</b> <b>{orders['price']}</b> * <b>{orders['miqdor']}</b> = <b>{int(orders['price']) * int(orders['miqdor'])}</b>"
        pay_status = []
        for method in order:
            if method['payment_status'] == "To'langan":
                pay_status.append(f"✅ To'langan")
            else:
                pay_status.append(f"❌ To'lanmagan")

            if method['status'] == "Olib ketish mumkin":
                pay_status.append(f'✅ Olib ketish mumkin')
            elif method['status'] == "Tayyorlanmoqda":
                pay_status.append(f'❌ Tayyorlanmoqda')
            elif method['status'] == "Xaridorga topshirilgan":
                pay_status.append(f'{method["status"]}')
            elif method['status'] == "Yo'lda":
                pay_status.append(f"🚚 Yo'lda")

            adminga += f"💸 To'lov Turi: {method['payment_method']}\n"
            break
        adminga += f"💰 Ja'mi: {total}\n"
        adminga += f"💲 To'lov Holati: {pay_status[0]}\n"
        adminga += f"‼️ Status: <b>{pay_status[1]}</b>"
        bttn = InlineKeyboardMarkup(row_width=1)
        if pay_status[1] == f"✅ Olib ketish mumkin" or pay_status[1] == "🚚 Yo'lda":
            bttn.insert(InlineKeyboardButton(text=f'✅ Xaridorga topshirildi', callback_data=f'{chat_id}_{message.text}_filial_gave'))
        elif pay_status[1] == '❌ Tayyorlanmoqda':
            bttn.insert(InlineKeyboardButton(text=f'✅ Tayyor', callback_data=f'{chat_id}_{message.text}_filial'))

        await message.answer(text=f"Buyurtma", reply_markup=admins_panel)
        await message.answer(text=adminga, reply_markup=bttn)
    else:
        await message.answer(text=f"😕 Bunday raqamli buyurtma topilmadi!", reply_markup=admins_panel)
    await state.finish()

@dp.message_handler(commands='users')
async def get_all_users_handler(message: types.Message, state: FSMContext):
    if message.chat.id == 5596277119:
        ozimga = f"👥 Barcha userlar\n"
        total_users = 0
        for i in await get_all_users():
            ozimga += f"\n<b>{i['id']}</b> <b>{i['full_name'][0:len(i['full_name'])//2]}</b>... <b>{i['username']}</b> <code>{i['phone_number']}</code>"
            total_users += 1
        ozimga += f"\n\n👥 Ja'mi: <b>{total_users}</b>"
        await message.answer(text=ozimga)
    else:
        await message.answer(text=f"🚫🙅 ‍️Access is prohibited")

@dp.message_handler(commands='users_buys')
async def get_history_buys_only_me_handler(message: types.Message, state: FSMContext):
    if message.chat.id == 5596277119:
        await message.answer(text=f"CHAT_ID yoki TELEFON RAQAM yoki USERNAME")
        await state.set_state('enter_data_to_me')
    else:
        await message.answer(text=f"🚫🙅 ‍️Access is prohibited")

@dp.message_handler(state=f'enter_data_to_me')
async def getting_data_to_me_handler(message: types.Message, state: FSMContext):
    user = await get_data_to_me(text=message.text)
    user_buys = await get_user_buys(chat_id=user['chat_id'])
    ozimga = ""
    if user_buys:
        ozimga = f"Buyurtmalar: \n"
        for user in user_buys:
            ozimga += f"\n{user['product']} -> {user['miqdor']} * {user['price']} | <b>{user['bought_at']}</b> <b>{user['which_filial'] if user['which_filial'] != 'null' else None}</b>"
    else:
        ozimga = f"Buyurtmalar topilmaadi... -_-"
    await message.answer(text=ozimga)
    await state.finish()