import sqlalchemy
from main.database_set import metadata

users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("full_name", sqlalchemy.String),
    sqlalchemy.Column("username", sqlalchemy.String),
    sqlalchemy.Column("lang", sqlalchemy.String),
    sqlalchemy.Column("phone_number", sqlalchemy.String),
    sqlalchemy.Column("chat_id", sqlalchemy.BigInteger)
)

menu = sqlalchemy.Table(
    "menu",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('menu_picture', sqlalchemy.String),
    sqlalchemy.Column("menu_name", sqlalchemy.String),
    sqlalchemy.Column("lang", sqlalchemy.String),
)

logo = sqlalchemy.Table(
    'logo',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('photo', sqlalchemy.String)
)

fast_food_menu = sqlalchemy.Table(
    "fast_food_menu",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("menu", sqlalchemy.String),
    sqlalchemy.Column("food_name", sqlalchemy.String),
    sqlalchemy.Column("description", sqlalchemy.String),
    sqlalchemy.Column("price", sqlalchemy.Integer),
    sqlalchemy.Column("photo", sqlalchemy.String)
)

admins = sqlalchemy.Table(
    'admins',
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('chat_id', sqlalchemy.BigInteger),
    sqlalchemy.Column('name', sqlalchemy.String)
)

curers = sqlalchemy.Table(
    "curers",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("chat_id", sqlalchemy.BigInteger, nullable=True),
    sqlalchemy.Column("status", sqlalchemy.String, nullable=True)
)

basket = sqlalchemy.Table(
    "basket",
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("product", sqlalchemy.String),
    sqlalchemy.Column("menu_name", sqlalchemy.String),
    sqlalchemy.Column("miqdor", sqlalchemy.Integer),
    sqlalchemy.Column("narx", sqlalchemy.BigInteger),
    sqlalchemy.Column("chat_id", sqlalchemy.BigInteger)
)

filials = sqlalchemy.Table(
    'filials',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('filial_name', sqlalchemy.String),
    sqlalchemy.Column('latitude', sqlalchemy.String),
    sqlalchemy.Column('longitude', sqlalchemy.String),
    sqlalchemy.Column('lang', sqlalchemy.String),
    sqlalchemy.Column('is_open', sqlalchemy.Boolean)
)

locations = sqlalchemy.Table(
    "locations",
    metadata,
    sqlalchemy.Column("location_name", sqlalchemy.String),
    sqlalchemy.Column("latitude", sqlalchemy.String),
    sqlalchemy.Column("longitude", sqlalchemy.String),
    sqlalchemy.Column("chat_id", sqlalchemy.BigInteger)
)

payments = sqlalchemy.Table(
    'payments',
    metadata,
    sqlalchemy.Column("payment_name", sqlalchemy.String),
    sqlalchemy.Column("status", sqlalchemy.Boolean),
    sqlalchemy.Column('lang', sqlalchemy.String)
)

ordering = sqlalchemy.Table(
    'ordering',
    metadata,
    sqlalchemy.Column('chat_id', sqlalchemy.BigInteger),
    sqlalchemy.Column('status', sqlalchemy.Boolean)
)

history_buys = sqlalchemy.Table(
    "history_buys",
    metadata,
    sqlalchemy.Column("number", sqlalchemy.BigInteger),
    sqlalchemy.Column("product", sqlalchemy.String),
    sqlalchemy.Column("miqdor", sqlalchemy.Integer),
    sqlalchemy.Column("price", sqlalchemy.Integer),
    sqlalchemy.Column("bought_at", sqlalchemy.DateTime),
    sqlalchemy.Column("status", sqlalchemy.String),
    sqlalchemy.Column("payment_method", sqlalchemy.String),
    sqlalchemy.Column("payment_status", sqlalchemy.String),
    sqlalchemy.Column("go_or_order", sqlalchemy.String),
    sqlalchemy.Column("which_filial", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("chat_id", sqlalchemy.BigInteger),
    sqlalchemy.Column("sent", sqlalchemy.Boolean, default=False)
)

filial_admins = sqlalchemy.Table(
    'filial_admins',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('which_filial', sqlalchemy.String),
    sqlalchemy.Column('admin_name', sqlalchemy.String),
    sqlalchemy.Column('chat_id', sqlalchemy.BigInteger)
)

curer_orders = sqlalchemy.Table(
    'curer_orders',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('number', sqlalchemy.BigInteger),
    sqlalchemy.Column('chat_id', sqlalchemy.BigInteger),
    sqlalchemy.Column('latitude', sqlalchemy.String),
    sqlalchemy.Column('longitude', sqlalchemy.String)
)

order_number = sqlalchemy.Table(
    'order_number',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('number', sqlalchemy.BigInteger),
    sqlalchemy.Column('chat_id', sqlalchemy.BigInteger),
)

about_we = sqlalchemy.Table(
    'about_we',
    metadata,
    sqlalchemy.Column('about_we', sqlalchemy.String)
)

socials = sqlalchemy.Table(
    'socials',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('social_name', sqlalchemy.String),
    sqlalchemy.Column('link', sqlalchemy.String),
)

message_for_user = sqlalchemy.Table(
    'message_for_user',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('message_uz', sqlalchemy.String),
    sqlalchemy.Column('message_ru', sqlalchemy.String)
)

radius = sqlalchemy.Table(
    'radius',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('radius', sqlalchemy.Integer),
    sqlalchemy.Column('sum', sqlalchemy.Integer)
)
