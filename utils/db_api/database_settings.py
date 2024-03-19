from lang import translate_uz_to_ru
from main.database_set import database
from main.models import *

async def get_user(chat_id):
    return await database.fetch_one(query=users.select().where(users.c.chat_id==chat_id))



async def insert_user(data: dict):
    return await database.execute(query=users.insert().values(
        full_name=data["full_name"],
        username=data["username"],
        lang=data["lang"],
        phone_number=data["phone_number"],
        chat_id=data["chat_id"],
    ))

async def get_main_menu_logo():
    return await database.fetch_one(query=logo.select())

async def get_menu():
    return await database.fetch_all(query=menu.select().where(menu.c.lang=='uz'))

async def get_menu_ru():
    return await database.fetch_all(query=menu.select().where(menu.c.lang=='ru'))

async def get_fast_foods_in_menu(menu_name):
    return await database.fetch_all(query=fast_food_menu.select().where(fast_food_menu.c.menu==menu_name))

async def get_user_miqdor(chat_id, fast_food, menu_name):
    return await database.fetch_one(query=basket.select().where(basket.c.product==fast_food, basket.c.menu_name==menu_name, basket.c.chat_id==chat_id))

async def get_user_basket(chat_id):
    return await database.fetch_all(query=basket.select().where(basket.c.chat_id==chat_id))

async def update_product_miqdor(miqdor, product_name, chat_id, menu_name, narx):
    new_miqdor = int(miqdor) + 1
    return await database.execute(query=basket.update().values(
        miqdor=new_miqdor,
        narx=narx*new_miqdor
    ).where(basket.c.chat_id==chat_id, basket.c.product==product_name, basket.c.menu_name==menu_name))


async def update_product_miqdor_minus(miqdor, product_name, chat_id, menu_name, now_price):
    if miqdor == 1:
        return await database.execute(query=basket.delete().where(basket.c.chat_id==chat_id, basket.c.product==product_name, basket.c.menu_name==menu_name))
    else:
        new_price = now_price // miqdor
        return await database.execute(query=basket.update().values(
            miqdor=miqdor - 1,
            narx=now_price - new_price
        ).where(basket.c.chat_id == chat_id, basket.c.product == product_name, basket.c.menu_name == menu_name))

async def get_fast_food_in_menu(fast_food_name, menu_name):
    return await database.fetch_one(query=fast_food_menu.select().where(fast_food_menu.c.food_name==fast_food_name, fast_food_menu.c.menu==menu_name))

async def is_admin(chat_id):
    return await database.fetch_one(query=admins.select().where(admins.c.chat_id==chat_id))

async def get_menu_pic(menu_name):
    return await database.fetch_one(query=menu.select().where(menu.c.menu_name==menu_name))

async def add_meal_to_menu(data: dict):
    return await database.execute(query=fast_food_menu.insert().values(
        menu=f"{data['menu']}",
        food_name=f"{data['name']}",
        price=data['price'],
        photo=data['photo'],
        description=data['desc_uz']
    ))

async def get_all_filials(lang):
    return await database.fetch_all(query=filials.select().where(filials.c.lang==lang, filials.c.is_open==True))

async def get_filial(filial_name):
    return await database.fetch_one(query=filials.select().where(filials.c.filial_name==filial_name))

async def get_filial_admin(filial_name):
    return await database.fetch_all(query=filial_admins.select().where(filial_admins.c.which_filial==filial_name))

async def delete_filial_admin(data: dict):
    await database.execute(query=filial_admins.delete().where(
        filial_admins.c.which_filial==data['filial_name'],
        filial_admins.c.admin_name==data['admin_name']
    ))
    await database.execute(query=admins.delete().where(
        admins.c.name==data['admin_name']
    ))


async def add_meal_to_menu_ru(data: dict):
    return await database.execute(query=fast_food_menu.insert().values(
        menu=f"{data['menu_ru']}",
        food_name=f"{data['name_ru']}",
        price=data['price'],
        photo=data['photo'],
        description=data['desc_ru']
    ))

async def get_lat_long(chat_id, location_name):
    return await database.fetch_one(query=locations.select().where(locations.c.location_name==location_name, locations.c.chat_id==chat_id))

async def delete_meal(data: dict):
    return await database.execute(query=fast_food_menu.delete().where(
        fast_food_menu.c.menu == data['menu'],
        fast_food_menu.c.food_name == data['meal']
    ))
async def add_new_menu(data: dict):
    return await database.execute(query=menu.insert().values(
        menu_name=data['new_menu_name'],
        menu_picture=data['pic'],
        lang='uz'
    ))

async def add_new_menu_ru(data: dict):
    return await database.execute(query=menu.insert().values(
        menu_name=data['new_menu_name_ru'],
        menu_picture=data['pic'],
        lang='ru'
    ))

async def update_menu_name(data: dict):
    return await database.execute(query=menu.update().values(
        menu_name=data['new_name']
    ).where(menu.c.menu_name==data['menu']))

async def update_menu_name_ru(data: dict):
    return await database.execute(query=menu.update().values(
        menu_name=data['new_name_ru']
    ).where(menu.c.menu_name==data['menu_ru']))

async def update_menu_name_(data: dict):
    return await database.execute(query=fast_food_menu.update().values(
        menu_name=data['new_name']
    ).where(fast_food_menu.c.menu==data['menu']))

async def update_menu_name_ru_(data: dict):
    return await database.execute(query=fast_food_menu.update().values(
        menu_name=data['new_name_ru']
    ).where(fast_food_menu.c.menu==data['menu_ru']))

async def delete_menu(menu_name, rus_menu_name):
    return await database.execute(query=menu.delete().where(menu.c.menu_name==menu_name)), database.execute(query=fast_food_menu.delete().where(fast_food_menu.c.menu==menu_name)), database.execute(query=menu.delete().where(menu.c.menu_name==rus_menu_name)), database.execute(query=fast_food_menu.delete().where(fast_food_menu.c.menu==rus_menu_name))

async def update_meal_price(new_price, menu_name, rus_menu_name, food_name):
    return await database.execute(query=fast_food_menu.update().values(
        price=new_price
    ).where(fast_food_menu.c.menu==menu_name, fast_food_menu.c.food_name==food_name)), await database.execute(query=fast_food_menu.update().values(
        price=new_price
    ).where(fast_food_menu.c.menu==rus_menu_name))

async def update_meal_photo(new_photo, menu_name, rus_menu_name, food_name):
    return await database.execute(query=fast_food_menu.update().values(
        photo=new_photo
    ).where(fast_food_menu.c.menu==menu_name, fast_food_menu.c.food_name==food_name)), await database.execute(query=fast_food_menu.update().values(
        photo=new_photo
    ).where(fast_food_menu.c.menu==rus_menu_name))

async def update_meal_name(new_name, menu_name, rus_menu_name, food_name):
    return await database.execute(query=fast_food_menu.update().values(
        food_name=new_name
    ).where(fast_food_menu.c.menu==menu_name, fast_food_menu.c.food_name==food_name)), await database.execute(query=fast_food_menu.update().values(
        food_name=new_name
    ).where(fast_food_menu.c.menu==rus_menu_name))

async def add_admin_to_db(data: dict):
    return await database.execute(query=admins.insert().values(
        chat_id=data['chat_id'],
        name=data['name']
    ))

async def add_admin_filial(data: dict):
    await database.execute(query=filial_admins.insert().values(
        which_filial=data['filial_name'],
        chat_id=data['chat_id'],
        admin_name=data['admin_name']
    ))
    await database.execute(query=filial_admins.insert().values(
        which_filial=translate_uz_to_ru(text=data['filial_name']),
        chat_id=data['chat_id'],
        admin_name=data['admin_name']
    ))
    await database.execute(query=admins.insert().values(
        chat_id=data['chat_id'],
        name=data['admin_name']
    ))

async def get_all_admins():
    return await database.fetch_all(query=admins.select())

async def dl_admin(chat_id):
    return await database.execute(query=admins.delete().where(admins.c.chat_id==chat_id))

async def get_all_curers():
    return await database.fetch_all(query=curers.select())

async def insert_curer(data: dict):
    return await database.execute(query=curers.insert().values(
        name=data['name'],
        chat_id=data['chat_id'],
        status='Not Work'
    ))

async def del_curer(data: dict):
    if str(data['name']).isdigit():
        return await database.execute(query=curers.delete().where(curers.c.chat_id==int(data['name'])))
    else:
        return await database.execute(query=curers.delete().where(curers.c.name==data['name']))

async def get_product_in_basket(chat_id, menu_name, food_name):
    return await database.fetch_one(query=basket.select().where(basket.c.chat_id==chat_id, basket.c.product==food_name, basket.c.menu_name==menu_name))

async def is_in_basket(food_name, chat_id, menu_name):
    return await database.fetch_one(query=basket.select().where(basket.c.product==food_name, basket.c.menu_name==menu_name, basket.c.chat_id==chat_id))


async def add_product_to_basket(menu_name, food_name, narx, chat_id):
    return await database.execute(query=basket.insert().values(
        product=food_name,
        chat_id=chat_id,
        narx=narx,
        menu_name=menu_name,
        miqdor=1,
    ))

async def delete_product_from_basket(chat_id, product):
    return await database.execute(query=basket.delete().where(basket.c.chat_id==chat_id, basket.c.product==product))

async def get_user_location(location_name, chat_id):
    return await database.fetch_one(query=locations.select().where(locations.c.location_name==location_name and locations.c.chat_id==chat_id))

async def add_new_location_to_db(location_name, latitude, longitude, chat_id):
    location_exists = await database.fetch_one(query=locations.select().where((locations.c.location_name == location_name) & (locations.c.chat_id == chat_id)))
    if not location_exists:
        return await database.execute(query=locations.insert().values(
            location_name=str(location_name),
            longitude=f"a{longitude}a",
            latitude=f"a{latitude}a",
            chat_id=chat_id,
        ))



async def bosh_curer():
    return await database.fetch_one(query=curers.select().where(curers.c.status=='Not Work'))

async def select_payments():
    return await database.fetch_all(query=payments.select().where(payments.c.status==True))

async def turning_off_payment(payment_name):
    return await database.execute(query=payments.update().values(
        status=False
    ).where(payments.c.payment_name==payment_name))

async def add_payment_method(new_payment_name):
    return await database.execute(query=payments.insert().values(
        payment_name=new_payment_name,
        status=True
    ))

async def delete_payment(payment_name):
    return await database.execute(query=payments.delete().where(payments.c.payment_name==payment_name))

async def add_user_to_order(chat_id):
    if await database.fetch_one(query=ordering.select().where(ordering.c.chat_id==chat_id)):
        pass
    else:
        return await database.execute(query=ordering.insert().values(
            chat_id=chat_id,
            status=True
        ))

async def update_user_status_order(chat_id):
    return await database.execute(query=ordering.update().values(
        status=False
    ).where(ordering.c.chat_id==chat_id))

async def update_user_name(chat_id, new_name):
    return await database.execute(query=users.update().values(
        full_name=new_name
    ).where(users.c.chat_id==chat_id))

async def update_user_lang(new_lang, chat_id):
    return await database.execute(query=users.update().values(
        lang=new_lang
    ).where(users.c.chat_id==chat_id))

async def update_user_number(new_number, chat_id):
    return await database.execute(query=users.update().values(
        phone_number=new_number
    ).where(users.c.chat_id==chat_id))

async def false_payments():
    return await database.fetch_all(query=payments.select().where(payments.c.status==False))

async def update_payment_status(payment_name):
    return await database.execute(query=payments.update().values(
        status=True
    ).where(payments.c.payment_name==payment_name))

async def update_user_status(chat_id):
    return await database.execute(query=ordering.update().values(
        status=False
    ).where(ordering.c.chat_id==chat_id))

async def update_main_photo(new_photo):
    if await database.fetch_one(query=logo.select()):
        return await database.execute(query=logo.update().values(
            photo=new_photo
        ))
    else:
        return await database.execute(query=logo.insert().values(
            photo=new_photo
            ))

async def add_number_buys(number, chat_id):
    return await database.execute(query=order_number.insert().values(
        number=number,
        chat_id=chat_id
    ))

async def get_all_orders(chat_id):
    return await database.fetch_all(query=order_number.select().where(
        order_number.c.chat_id==chat_id
    ))

async def get_all_socials():
    return await database.fetch_all(query=socials.select())

async def add_social(data: dict):
    return await database.execute(query=database.execute(query=socials.insert().values(
        social_name=data['social_name'],
        link=data['link']
    )))

async def change_about(new_about):
    if await database.fetch_one(query=about_we.select()):
        return await database.execute(query=about_we.update().values(
            about_we=new_about
        ))
    else:
        return await database.execute(query=about_we.insert().values(
            about_we=new_about
        ))

async def get_about_we():
    return await database.fetch_one(query=about_we.select())

async def add_history_buys(chat_id, number, miqdor, product, price, bought_at, status, pay, payment_status,go_or_order, which_filial):
    return await database.execute(query=history_buys.insert().values(
        number=number,
        product=product,
        miqdor=miqdor,
        price=price,
        bought_at=bought_at,
        status=status,
        payment_method=pay[2:],
        payment_status=payment_status,
        go_or_order=go_or_order,
        which_filial=which_filial,
        chat_id=chat_id
    ))

async def delete_user_basket(chat_id):
    return await database.execute(query=basket.delete().where(basket.c.chat_id==chat_id))

async def get_user_locations(chat_id):
    return await database.fetch_all(query=locations.select().where(locations.c.chat_id==chat_id))


async def add_count_to_curer(chat_id):
    last_num = await database.fetch_one(query=curers.select().where(curers.c.chat_id==chat_id))
    num = 0
    last = last_num[3]
    if int(last[-1]) >= 1:
        num = last[-1]
        return await database.execute(query=curers.update().values(
            status=f"Work {int(num) + 1}"
        ).where(curers.c.chat_id==chat_id))
    else:
        return await database.execute(query=curers.update().values(
            status=f"Work 1"
        ).where(curers.c.chat_id==chat_id))

async def get_about_product(random_number):
    return await database.fetch_all(query=history_buys.select().where(history_buys.c.number==random_number))

async def update_buy(random_number, chat_id):
    curer_num = await database.fetch_one(query=curers.select().where(curers.c.chat_id==chat_id))
    curer_number = int(curer_num['status'][-1])
    if int(curer_number) == 1:
        await database.execute(
            history_buys.update()
            .values(
                status="Foydalanuvchiga topshirilgan.",
                payment_status="To'langan"
            )
            .where(history_buys.c.number == int(random_number))
        )
        await database.execute(
            curers.update()
            .values(status='Not Work')
            .where(curers.c.chat_id == chat_id)
        )
    elif int(curer_number) > 1:
        await database.execute(
            history_buys.update()
            .values(
                status="Foydalanuvchiga topshirilgan.",
                payment_status="To'langan"
            )
            .where(history_buys.c.number == int(random_number))
        )
        await database.execute(
            curers.update()
            .values(status=f"Work {curer_number - 1}")
            .where(curers.c.chat_id == chat_id)
        )

async def update_buy_filial(number: int, chat_id: int):
    return await database.execute(query=history_buys.update().values(
        status=f'Olib ketish mumkin'
    ).where(history_buys.c.number==number, history_buys.c.chat_id==chat_id))

async def update_buy_filial2(number, chat_id):
    return await database.execute(query=history_buys.update().values(
        status=f'Xaridorga topshirilgan',
        payment_status="To'langan"
    ).where(history_buys.c.number==number, history_buys.c.chat_id==chat_id))

async def add_order_curer(number, chat_id, latitude, longitude):
    return await database.execute(query=curer_orders.insert().values(
        number=number,
        chat_id=chat_id,
        latitude=latitude,
        longitude=longitude
    ))

async def get_close_filials():
    return await database.fetch_all(query=filials.select().where(filials.c.is_open==False, filials.c.lang=='uz'))

async def add_new_filial(data):
    await database.execute(query=filials.insert().values(
        filial_name=data['filial_name'],
        latitude=f"{data['latitude']}a",
        longitude=f"{data['longitude']}a",
        lang="uz",
        is_open=True
    ))
    await database.execute(query=filials.insert().values(
        filial_name=data['filial_name_ru'],
        latitude=f"{data['latitude']}a",
        longitude=f"{data['longitude']}a",
        lang="ru",
        is_open=True
    ))

async def close_filial(filial_name, filial_name_ru):
    await database.execute(query=filials.update().values(
        is_open=False
    ).where(filials.c.filial_name==filial_name))
    await database.execute(query=filials.update().values(
        is_open=False
    ).where(filials.c.filial_name==filial_name_ru))

async def del_filial(data: dict):
    await database.execute(query=filials.delete().where(filials.c.filial_name==data['filial_name_uz']))
    await database.execute(query=filials.delete().where(filials.c.filial_name==data['filial_name_ru']))
async def open_filial(filial_name, filial_name_ru):
    await database.execute(query=filials.update().values(
        is_open=True
    ).where(filials.c.filial_name==filial_name))
    await database.execute(query=filials.update().values(
        is_open=True
    ).where(filials.c.filial_name==filial_name_ru))

async def get_order_with_id(order_number):
    return await database.fetch_all(query=history_buys.select().where(
        history_buys.c.number==order_number
    ))