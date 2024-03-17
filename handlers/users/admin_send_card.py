from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove

from keyboards.default.default_keyboards import cancel_uz, admins_panel, main_menu_uzb
from keyboards.inline.inline_keyboards import paymented_rus, paymented
from loader import dp, types
from utils.db_api.database_settings import update_user_status_order, get_user, get_user_basket, is_admin, \
    get_about_product, update_buy, update_buy_filial, update_buy_filial2


@dp.callback_query_handler()
async def send_card_to_user(call: types.CallbackQuery, state: FSMContext):
    if call.data.isdigit():
        await update_user_status_order(chat_id=int(call.data))
        user = await get_user(chat_id=int(call.data))
        if user[3] == "uz":
            await dp.bot.send_message(chat_id=int(call.data),
                                      text=f"😊 Iltimos kuting admin sizga plastik karta tashlamoqda ...",
                                      reply_markup=ReplyKeyboardRemove())
        else:
            await dp.bot.send_message(chat_id=int(call.data),
                                      text=f"😊 Пожалуйста подождите, администратор кидает вам пластиковую карту ...",
                                      reply_markup=ReplyKeyboardRemove())
        await state.update_data({
            'chat_id': int(call.data)
        })
        await call.message.answer(text='😊 Foydalanuvchiga karta yuboring...', reply_markup=cancel_uz)
        await state.set_state('admin_sending_card')
    elif call.data.endswith('_filial'):
        data = call.data.split('_')

        await update_buy_filial(number=int(data[1]), chat_id=int(data[0]))
        filial = f""
        for i in await get_about_product(random_number=int(data[1])):
            filial = f"{i['which_filial']}"
        user = await get_user(chat_id=int(data[0]))
        if user[3] == "uz":
            await dp.bot.send_message(chat_id=int(data[0]),
                                      text=f"😊 Sizning: {data[1]} raqamli buyurtmangiz <b>{filial}</b> Filialimizda kutmoqda olib ketishingiz mumkin.")
        else:
            await dp.bot.send_message(chat_id=int(data[0]),
                                      text=f"😊 Ваш заказ под номером {data[1]} можно забрать в нашем филиале <b>{filial}</b>")
        await call.message.answer(text=f"✅ Foydalanuvchiga buyurtma tayyorligi haqida habar yuborildi.",
                                  reply_markup=admins_panel)
    elif call.data.endswith('_gave'):
        data = call.data.split('_')
        print(data)
        await update_buy_filial2(number=int(data[1]), chat_id=int(data[0]))
        user = await get_user(chat_id=int(data[0]))
        if user[3] == "uz":
            await dp.bot.send_message(chat_id=int(data[0]),
                                      text=f'😊 Sizning: {data[1]} raqamli buyurtmangiz xaridorga topshirildi.')
        else:
            await dp.bot.send_message(chat_id=int(data[0]),
                                      text=f'😊 Ваш заказ под номером {data[1]} был передан покупателю.')
        await call.message.answer(text=f'✅ Xabar yuborildi')
    elif call.data.endswith('_curer'):
        data = call.data.split("_")
        await update_buy(random_number=int(data[1]), chat_id=call.message.chat.id)

        await call.message.answer(text=f'Ok 👌')


@dp.message_handler(state='admin_sending_card')
async def sending_card_to_user(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = await get_user(chat_id=data['chat_id'])
    user_basket = await get_user_basket(chat_id=data['chat_id'])
    total = 0
    for basket in user_basket:
        total += basket['narx']
    if lang[3] == "uz":
        userga = f"😊 Admin sizga karta raqamini tashladi: {message.text}\n💸 Kartaga: <b>{total}</b> miqdorda pul o'tkazing "
        await dp.bot.send_message(chat_id=data['chat_id'], text=userga, reply_markup=paymented)
    else:
        userga = f"😊 Админ кинул вам карточку: {message.text}\n💸 Переведите <b>{total}</b> сум на этот номер карты."
        await dp.bot.send_message(chat_id=data['chat_id'], text=userga, reply_markup=paymented_rus)

    await message.answer(text="✅ Foydalanuvchiga karta raqami yuborildi.", reply_markup=admins_panel)
    await state.finish()
