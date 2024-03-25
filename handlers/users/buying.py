import random

from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from handlers.users.location import get_location_name, get_location_name_ru
from keyboards.default.default_keyboards import locations, locations_ru, yes_no_def, yes_no_def_ru, main_menu_uzb, \
    waiting_card_uz, waiting_card_ru, main_menu_rus, go_or_ordering, go_or_ordering_ru
from lang import translate_uz_to_ru
from loader import dp, types
from utils.db_api.database_settings import get_user, add_new_location_to_db, select_payments, get_user_locations, \
    add_user_to_order, bosh_curer, delete_user_basket, get_all_curers, get_user_basket, \
    get_all_filials, get_lat_long, get_filial, get_filial_admin, get_all_admins, add_history_buys, add_order_curer, \
    add_count_to_curer, get_order_with_id, add_number_buys


@dp.message_handler(state='in_basket', text="🛍 Buyurtma berish")
async def buy_product_handler(message: types.Message, state: FSMContext):
    userga = f"🤗 Buyurtmangiz turini tanlang."
    await message.answer(text=userga, reply_markup=go_or_ordering)
    await state.set_state('go_or_ordering')


@dp.message_handler(state='in_basket', text="🛍 Разместить заказ")
async def buy_product_handler(message: types.Message, state: FSMContext):
    userga = f"🤗 Выберите тип вашего заказа"
    await message.answer(text=userga, reply_markup=go_or_ordering_ru)
    await state.set_state('go_or_ordering')


@dp.message_handler(state=f"go_or_ordering")
async def go_or_ordering_handler(message: types.Message, state: FSMContext):
    lang = await get_user(chat_id=message.chat.id)
    if message.text[0] == "🏃":
        filials_bttn = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        counter = 0
        for count in await get_all_filials(lang=lang[3]):
            counter += 1
        await state.update_data({
            'go_or_order': message.text
        })
        for filial in await get_all_filials(lang=lang[3]):
            filials_bttn.insert(KeyboardButton(text=f"{filial['filial_name']}"))
        if lang[3] == "uz":
            filials_bttn.insert(KeyboardButton(text="❌ Bekor qilish"))
        else:
            filials_bttn.insert(KeyboardButton(text="❌ Отмена"))

        if lang[3] == "uz":
            await message.answer(text=f"Qaysi filialdan olib ketmoqchisiz?", reply_markup=filials_bttn)
        else:
            await message.answer(text=f"В каком филиале вы хотите забрать?", reply_markup=filials_bttn)
        await state.set_state('selecting_filial')
    else:
        if lang[3] == "uz":
            await message.answer(text=f"📍 Yetkazib berish joylashuvini kiriting yoki yuboring", reply_markup=locations)
        else:
            await message.answer(text=f"📍 Введите или выберите место доставки", reply_markup=locations_ru)
        await state.set_state('get_location')


@dp.message_handler(state=f"get_location", content_types=types.ContentType.LOCATION)
async def get_location_handler(message: types.Message, state: FSMContext):
    lang = await get_user(chat_id=message.chat.id)
    location = f""
    if lang[3] == "uz":
        loc = get_location_name(latitude=message.location.latitude, longitude=message.location.longitude)
        location = f"{loc[-1]} {loc[-3]} {loc[-5]} {loc[-4]} {loc[0]}"
        userga = f"‼️ Siz yuborgan manzil: <b>{location}</b> ushbu manzilni tasdiqlaysizmi?"
        await message.answer(text=userga, reply_markup=yes_no_def)
    else:
        loc = get_location_name_ru(latitude=message.location.latitude, longitude=message.location.longitude)
        location = f"{loc[-1]} {loc[-3]} {loc[-5]} {loc[-4]} {loc[0]}"
        userga = f"‼️ Адрес, который вы отправили: <b>{location}</b> подтвердить этот адрес?"
        await message.answer(text=userga, reply_markup=yes_no_def_ru)
    await state.update_data({
        "location_name": location,
        "longitude": message.location.longitude,
        "latitude": message.location.latitude,
        "chat_id": message.chat.id,
    })
    await state.set_state('accept')


@dp.message_handler(state='selecting_filial')
async def select_filial_handler(message: types.Message, state: FSMContext):
    lang = await get_user(chat_id=message.chat.id)
    if await get_filial_admin(filial_name=message.text):
        userga = f""
        await state.update_data({
            'filial': message.text
        })
        payments_bttn = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        for payment in await select_payments():
            if payment['payment_name'] == "Naqd" or payment['payment_name'] == "Наличные":
                payments_bttn.insert(KeyboardButton(text=f"💸 {payment['payment_name']}"))
            else:
                payments_bttn.insert(KeyboardButton(text=f"💴 {payment['payment_name']}"))

        if lang[3] == "uz":
            payments_bttn.insert(KeyboardButton(text=f"⬅️ Ortga"))
            userga = f"💸 Tolov turini tanlang."
        else:
            payments_bttn.insert(KeyboardButton(text=f"⬅️ Назад"))
            userga = f"💸 Выберите тип оплаты."
        await message.answer(text=userga, reply_markup=payments_bttn)
        await state.set_state('paying')
    else:
        userga = f""
        if lang[3] == 'uz':
            userga = f"❌ Kechirasiz siz noto'g'ri filial tanladingiz yoki bu filial hozirda yopiq."
        else:
            userga = f"❌ К сожалению, вы зашли не в тот филиал, или наш филиал в настоящее время закрыт."
        await message.answer(text=userga)
        await state.set_state('selecting_filial')


@dp.message_handler(state=f"accept")
async def get_location_handler(message: types.Message, state: FSMContext):
    lang = await get_user(chat_id=message.chat.id)
    data = await state.get_data()
    if message.text[0] == "✅":
        await state.update_data({
            "location_name": data['location_name'],
            "longitude": data['longitude'],
            "latitude": data['latitude'],
            "chat_id": data['chat_id'],
        })
        await add_new_location_to_db(location_name=translate_uz_to_ru(text=data['location_name']),
                                     latitude=data['latitude'], longitude=data["longitude"], chat_id=data['chat_id'])
        payments_bttn = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        for payment in await select_payments():
            if payment['payment_name'] == "Naqd" or payment['payment_name'] == "Наличные":
                payments_bttn.insert(KeyboardButton(text=f"💸 {payment['payment_name']}"))
            else:
                payments_bttn.insert(KeyboardButton(text=f"💴 {payment['payment_name']}"))

        if lang[3] == "uz":
            payments_bttn.insert(KeyboardButton(text=f"❌ Bekor qilish"))
            userga = f"💸 Tolov turini tanlang."
        else:
            payments_bttn.insert(KeyboardButton(text=f"❌ Отмена"))
            userga = f"💸 Выберите тип оплаты."
        await message.answer(text=userga, reply_markup=payments_bttn)
        await state.set_state('paying')
    else:
        if lang[3] == "uz":
            userga = f"‼️ Aniq manzilni yuborng."
        else:
            userga = f"‼️ Пожалуйста, пришлите точный адрес."
        await message.answer(text=userga, reply_markup=locations)
        await state.set_state('get_location')


@dp.message_handler(state=f"get_location")
async def get_location_handler(message: types.Message, state: FSMContext):
    lang = await get_user(chat_id=message.chat.id)
    user_locations = await get_user_locations(chat_id=message.chat.id)
    if user_locations:
        locatinos_bttn = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        for locat in await get_user_locations(chat_id=message.chat.id):
            locatinos_bttn.insert(KeyboardButton(text=locat['location_name']))
        if lang[3] == "uz":
            locatinos_bttn.insert(KeyboardButton(text=f"❌ Bekor qilish"))
            userga = f"😊 O'zingizga qulay manzilni tanlang."
            await message.answer(text=userga, reply_markup=locatinos_bttn)
        else:
            locatinos_bttn.insert(KeyboardButton(text=f"❌ Отмена"))
            userga = f"😊 Выберите адрес, который удобен для вас."
            await message.answer(text=userga, reply_markup=locatinos_bttn)
        await state.set_state('select_locations')
    else:
        if lang[3] == "uz":
            userga = f"😕 Kechirasiz bizning botda sizning manzillaringiz mavjud emas."
            await message.answer(text=userga, reply_markup=locations)
        else:
            userga = f"😕 К сожалению, ваши адреса недоступны в нашем боте."
            await message.answer(text=userga, reply_markup=locations_ru)
        await state.set_state('get_location')


@dp.message_handler(state=f'select_locations')
async def get_loc_long_lat_handler(message: types.Message, state: FSMContext):
    lat_long = await get_lat_long(location_name=message.text, chat_id=message.chat.id)
    await state.update_data({
        'location_name': message.text,
        'latitude': lat_long['latitude'][1:-1],
        'longitude': lat_long['longitude'][1:-1],
        'chat_id': lat_long['chat_id']
    })
    lang = await get_user(chat_id=message.chat.id)
    payments = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    for pay in await select_payments():
        if pay['payment_name'] == "Naqd" or pay['payment_name'] == "Наличные":
            payments.insert(KeyboardButton(text=f"💸 {pay['payment_name']}"))
        else:
            payments.insert(KeyboardButton(text=f"💴 {pay['payment_name']}"))
    if lang[3] == "uz":
        await message.answer(text=f"😊 To'lov turini tanlang.", reply_markup=payments)
    else:
        await message.answer(text=f"😊 Выберите тип оплаты.", reply_markup=payments)
    await state.set_state('paying')


@dp.message_handler(state='paying')
async def paying_handler(message: types.Message, state: FSMContext):
    lang = await get_user(chat_id=message.chat.id)
    await state.update_data({
        'pay': message.text
    })
    data = await state.get_data()
    language = f""
    if lang[3] == "uz":
        language = f"🇺🇿 Uzbek tili"
    else:
        language = f"🇷🇺 Rus tili"

    total = 0
    random_number = random.randint(1000000, 10000000)
    while True:
        if await get_order_with_id(order_number=random_number):
            random_number = random.randint(1000000, 10000000)
        else:
            break
    curerga = f"""
👤 Toliq Ism: {lang[1]}
👤 Username: {lang[2]}
🌐 Til: {language}
📞 Telefon raqam: {lang[4]}
🆔 Buyurtma raqami: {random_number}
🛍 Mahsulotlar:\n
"""
    for product in await get_user_basket(chat_id=message.chat.id):
        total += int(product['narx'])
        curerga += f"<b>{product['product']}</b> {int(product['narx']) // int(product['miqdor'])} * {product['miqdor']} = {product['narx']}\n"
        await add_number_buys(chat_id=message.chat.id, number=random_number)
        if data.get('go_or_order'):
            await add_history_buys(chat_id=message.chat.id, number=random_number, miqdor=product['miqdor'],
                                   product=product['product'], price=product['narx'] // product['miqdor'],
                                   bought_at=message.date, status='Tayyorlanmoqda', pay=data['pay'],
                                   payment_status="To'lanmagan", go_or_order=data['go_or_order'][2:],
                                   which_filial=data['filial'])
        else:
            await add_history_buys(chat_id=message.chat.id, number=random_number, miqdor=product['miqdor'],
                                   product=product['product'], price=product['narx'] // product['miqdor'],
                                   bought_at=message.date, status='Tayyorlanmoqda', pay=data['pay'],
                                   payment_status="To'lanmagan", go_or_order="Dostavka",
                                   which_filial="null")
    curerga += f"\n💸 To'lov turi: <b>{data['pay']}</b>"
    curerga += f"\n💰 Ja'mi: <b>{total}</b>"
    if data.get('location_name'):
        curerga += f"\n📍 Joylashuv: <b>{data['location_name']}</b>"

    if data.get('go_or_order'):
        filial_admins = await get_filial_admin(data['filial'])
        tayyor = InlineKeyboardMarkup(row_width=1)
        tayyor.insert(
            InlineKeyboardButton(text='✅ Buyurtma tayyor', callback_data=f"{message.chat.id}_{random_number}_filial"))
        for admin in filial_admins:
            await dp.bot.send_message(chat_id=admin['chat_id'], text=curerga, reply_markup=tayyor)
        if lang[3] == "uz":
            userga = f"✅ Tabriklaymiz buyurtmangiz qabul qilindi.\n\n🆔Buyurtma raqamingiz: <b>{random_number}</b>\n🤗 Agar buyurtmangiz tayyor bo'lsa biz sizga xabar yuboramiz"
            await message.answer(text=userga, reply_markup=main_menu_uzb)
        else:
            userga = f" ✅ Поздравляем, ваш заказ принят.\n\n🆔Номер вашего заказа: <b>{random_number}</b>\n🤗 Мы отправим вам сообщение, когда ваш заказ будет готов"
            await message.answer(text=userga, reply_markup=main_menu_rus)
        await delete_user_basket(chat_id=message.chat.id)
        await state.finish()
    else:
        if message.text[0] != "💸":
            await state.update_data({
                'pay': message.text
            })
            adminga = f"Yangi buyurtma qabul qilindi foydalanuvchiga karta raqam tashlaysizmi?"
            admin_bttn = InlineKeyboardMarkup(row_width=1)
            admin_bttn.insert(InlineKeyboardButton(text="✅ Xa", callback_data=f"{message.chat.id}"))
            admins = await get_all_admins()
            for admin in admins:
                await dp.bot.send_message(chat_id=admin['chat_id'], text=adminga, reply_markup=admin_bttn)
            await add_user_to_order(chat_id=message.chat.id)
            if lang[3] == "uz":
                userga = f"😊 Sizning so'rovingiz adminlarga yuborildi.Tez orada adminlar sizga karta tashlaydi iltimos kuting.\n\nAgar kutishni hohlamasangiz '🚚🏃 Kuryer kelgach karta korsatsin' Tugmasini bosing shunda siz buyurtmangiz yetkazilgach tolov amalga oshirishingiz mumkin bo'ladi."
                await message.answer(text=userga, reply_markup=waiting_card_uz)
            else:
                userga = f"😊 Ваш запрос отправлен администраторам. Администраторы скоро вышлют вам карту. Пожалуйста, подождите.\n\nЕсли вы не хотите ждать, нажмите кнопку '🚚🏃 Когда курьер придет, покажите картудет' и Вы сможете произвести оплату при доставке заказа."
                await message.answer(text=userga, reply_markup=waiting_card_ru)
            await state.set_state('waiting_card')
        else:

            ishsiz_curer = await bosh_curer()
            ordered = InlineKeyboardMarkup(row_width=1)
            ordered.insert(
                InlineKeyboardButton(text=f"✅ Yetkazildi", callback_data=f"{message.chat.id}_{random_number}_curer"))
            if ishsiz_curer != None:
                await add_count_to_curer(chat_id=ishsiz_curer['chat_id'])
                await add_order_curer(number=random_number, chat_id=ishsiz_curer['chat_id'], latitude=data['latitude'],
                                      longitude=data['longitude'])
                await dp.bot.send_location(longitude=data['longitude'], latitude=data['latitude'],
                                           chat_id=ishsiz_curer['chat_id'])
                await dp.bot.send_message(chat_id=ishsiz_curer['chat_id'], text=curerga, reply_markup=ordered)
                if lang[3] == "uz":
                    await message.answer(text=f"✅ Buyurtmangiz qabul qilindi.", reply_markup=main_menu_uzb)
                else:
                    await message.answer(text=f"✅ Ваш заказ принят.", reply_markup=main_menu_rus)
            else:
                all_curers = await get_all_curers()
                curers = []
                for curer in all_curers:
                    curers.append(curer['chat_id'])
                random_curer = random.choice(curers)
                await add_count_to_curer(chat_id=random_curer)
                await dp.bot.send_location(longitude=data['longitude'], latitude=data['latitude'], chat_id=random_curer)
                await dp.bot.send_message(chat_id=random_curer, text=curerga, reply_markup=ordered)
                await add_order_curer(number=random_number, chat_id=random_curer, latitude=f"{data['latitude']}a",
                                      longitude=f"{data['longitude']}a")
                if lang[3] == "uz":
                    await message.answer(
                        text=f"✅😕 Buyurtmangiz qabul qilindi ammo bo'sh kuryer topilmaganligi sabab buyurtmangiz ozgina kechikishi mumkin.Noqulayliklar uchun uzr so'raymiz",
                        reply_markup=main_menu_uzb)
                else:
                    await message.answer(
                        text=f"✅😕 Ваш заказ принят, но доставка может немного задержаться, поскольку нам не удалось найти безработного курьера. Приносим извинения за неудобства",
                        reply_markup=main_menu_uzb)
            await delete_user_basket(chat_id=message.chat.id)
            await state.finish()
