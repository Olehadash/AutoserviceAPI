from flask import Flask, url_for, redirect, render_template, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required, current_user
from flask_security.utils import encrypt_password
import flask_admin
from flask_login import LoginManager
from flask_admin.contrib import sqla
from flask_admin import helpers as admin_helpers
from flask_admin import BaseView, expose
from wtforms import PasswordField
from werkzeug.middleware.shared_data import SharedDataMiddleware
from flask_bcrypt import Bcrypt
from twilio.rest import Client

# Create Flask application
app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)
login_manager = LoginManager(app)
bcrypt = Bcrypt(app)

# Initialize Twilio client
client = Client(app.config['TWILIO_ACCOUNT_SID'], app.config['TWILIO_AUTH_TOKEN'])

from AutoserviceAPI.model import Role, User, City, Category

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

from AutoserviceAPI.views import MyModelView, UserView, CustomView, CityView, CategoryView

# url rule for uppload
app.add_url_rule('/uploads/<filename>', 'uploaded_file',
                 build_only=True)
app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
    '/uploads':  app.config['UPLOAD_FOLDER']
})
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# Flask views
@app.route('/')
def index():
    return render_template('index.html')

# Create admin
admin = flask_admin.Admin(
    app,
    'My Dashboard',
    base_template='my_master.html',
    template_mode='bootstrap4',
)

# Add model views
admin.add_view(MyModelView(Role, db.session, menu_icon_type='fa', menu_icon_value='fa-server', name="Roles"))
admin.add_view(UserView(User, db.session, menu_icon_type='fa', menu_icon_value='fa-users', name="Users"))
admin.add_view(CityView(City, db.session, menu_icon_type='fa', menu_icon_value='fa-building', name="City"))
admin.add_view(CategoryView(Category, db.session, menu_icon_type='fa', menu_icon_value='fa-cubes', name="Category"))

# define a context processor for merging flask-admin's template context into the
# flask-security views.
@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
        get_url=url_for
    )

def build_sample_db():
    """
    Populate a small db with some example entries.
    """

    import string
    import random

    db.drop_all()
    db.create_all()

    with app.app_context():
        user_role = Role(name='customer')
        executor_role = Role (name='executor')
        super_user_role = Role(name='superuser')
        db.session.add(user_role)
        db.session.add(super_user_role)
        db.session.commit()

        test_user = user_datastore.create_user(
            name='Admin',
            email='admin',
            password=encrypt_password('admin'),
            roles=[super_user_role]
        )

        cities = ["Нур-Султан", "Алматы", "Шымкент", "Акистау", "Акколь", "Аксай", "Аксу","Актау", "Актобе", "Алга", "Арал", "Аркалык", "Арысь","Атбасар", "Атырау", "Байконыр", "Балхаш", "Бейнеу", "Ерейментау","Есик", "Жанаозен", "Жанатас", "Жаркент", "Жезказган","Житикара", "Зачаганск", "Индерборский","Казалы", "Кандыагаш","Капчагай", "Карабулак","Караганда", "Каражал","Каскелен","Кентау", "Кокшетау","Кордай", "Костанай", "Кульсары", "Курмангазы","Курчатов", "Кызылорда", "Ленгер", "Лисаковск", "Макат","Макинск", "Махамбет", "Мерке", "Мерке", "Павлодар","Петропавл","Риддер", "Рудный", "Сайхин", "Сарань", "Сарыагаш", "Сатпаев", "Семей","Степногорск", "Талапкер", "Талгар", "Талдыкорган","Тараз", "Текели", "Темиртау", "Туркестан", "Уральск", "Усть-Каменогорск","Ушарал", "Уштобе", "Федоровка", "Форт-Шевченко","Хромтау", "Шалкар", "Шардара", "Шахтинск","Шортанды", "Шу", "Щучинск", "Экибастуз"]

        for c in cities:
            new_city = City(name = c)
            db.session.add(new_city)

        categories = [
            {"name": "Услуги автосервиса", "description": "Услуги автосервиса", "parent_id": 0},
            {"name": "Сельхозтехника","description": "Сельхозтехника", "parent_id": 1},
            {"name": "Запчасти для крупной техники", "description": "Автобусы, Грузовые машины, Спецтехника", "parent_id": 0},
            {"name": "Автомойка", "description": "Автомойка","parent_id": 0},
            {"name": "Ремонт ходовой части", "description": "Ремонт ходовой части", "parent_id": 4 },
            {"name": "Замена масла/Фильтров", "description": "Замена масла/Фильтров", "parent_id": 4},
            {"name": "Развал-схождение", "description": "Развал-схождение", "parent_id": 4},
            {"name": "Автоэлектрик", "description": "Автоэлектрик", "parent_id": 4},
            {"name": "Ремонт по кузову", "description": "Ремонт по кузову", "parent_id": 4},
            {"name": "Ремонт двигателя/Моторист", "description": "Ремонт двигателя/Моторист", "parent_id": 4},
            {"name": "Ремонт АПП/КПП", "description": "Ремонт АПП/КПП", "parent_id": 4 },
            {"name": "Прошивка бортового компьютера","description": "Прошивка бортового компьютера","parent_id": 4},
            {"name": "Грузовые и автобусы", "description": "Грузовые и автобусы", "parent_id": 1},
            {"name": "Диагностика/Ремонт инжекторов/Моновспрыскивателей", "description": "Диагностика/Ремонт инжекторов/Моновспрыскивателей", "parent_id": 4},
            {"name": "Шиномонтаж/Балансировка", "description": "Шиномонтаж/Балансировка", "parent_id": 4},
            {"name": "Установка ГБО", "description": "Установка ГБО", "parent_id": 4},
            {"name": "Регулировка фар", "description": "регулировка фар", "parent_id": 4},
            {"name": "Тюнинг", "description": "тюнинг", "parent_id": 4},
            {"name": "Детайлинг", "description": "детайлинг", "parent_id": 4},
            {"name": "Ремонт глушителей", "description": "Ремонт глушителей", "parent_id": 4},
            {"name": "Двигатель и комплектующие", "description": "Поршни, колен.вал, ремни, клапаны, распред.вал и т.д.","parent_id": 18},
            {"name": "КПП/АКПП", "description": "Трансмиссия и составные части коробки передач", "parent_id": 18},
            {"name": "Топливная система", "description": "Карбюратор или инжектор, шланги, фильтр, форсунки и насос", "parent_id": 18},
            {"name": "Рулевое управление","description": "Рейка, колонка, тяга и рулевые наконечники", "parent_id": 18},
            {"name": "Подвеска", "description": "Амортизаторы сайлентблоки, стабилизаторы, опоры, шаровые и рычаги", "parent_id": 18},
            {"name": "Прочее", "description": "Прочее", "parent_id": 18},
            {"name": "Нотариус", "description": "Нотариус", "parent_id": 0},
            {"name": "Спецтехника", "description": "Спецтехника", "parent_id": 1},
            {"name": "Ремонт Рулевого управления", "description": "ГУР и т.д.", "parent_id": 4},
            {"name": "Аргонная сварка", "description": "Сварочные работы, КЕМПИ", "parent_id": 4},
            {"name": "Электронная диагностика автомашины", "description": "Электронная диагностика автомашины", "parent_id": 12},
            {"name": "Автозапчасти", "description": "Автозапчасти", "parent_id": 0},
            { "name": "Авторазбор", "description": "Склад  автомобильных запчастей", "parent_id": 18},
            {"name": "Электроника", "description": "Фары, противотуманки, электропроводка, внутреннее освещение и кондиционер", "parent_id": 18},
            {"name": "Тормозная система", "description": "Диски, колодки, шланги, суппорты и цилиндр", "parent_id": 18},
            {"name": "Жидкости", "description": "Моторное масло, трансмиссионное масло, тормозная жидкость, антифриз, смазки и т.д.","parent_id": 18},
            {"name": "Автостекла", "description": "Лобовое стекло, другие стекла", "parent_id": 18},
            {"name": "Комплектующие по кузову", "description": "Бампер, зеркала, двери и т.д.", "parent_id": 18},
            {"name": "Комплектующие по салону", "description": "Сидение, зеркало, панель и т.д.", "parent_id": 18},
            {"name": "Шины, Диски", "description": "Шины, Диски", "parent_id": 18},
            {"name": "Электроприводы", "description": "Аккумуляторы, генераторы, свечи зажигания", "parent_id": 18},
            {"name": "Автокраска", "description": "Краска, грунтовка, шкурка, шпатлевка", "parent_id": 18},
            {"name": "Аксессуары", "description": "Дворники, коврики, чехлы и т.д.", "parent_id": 18},
            {"name": "Услуги манипулятора", "description": "Услуги манипулятора", "parent_id": 0},
            {"name": "Техосмотр", "description": "Техосмотр", "parent_id": 0},
            {"name": "Страховой полис", "description": "Страховой полис", "parent_id": 0},
            {"name": "Автоломбард", "description": "Автоломбард", "parent_id": 0}
        ]

        for c in categories:
            new_category = Category(name = c["name"], description = c["description"], parent_id = c["parent_id"])
            db.session.add(new_category)

        db.session.commit()
    return

def start_verification(to, channel='sms'):
    if channel not in ('sms', 'call'):
        channel = 'sms'
    print(to)
    verify = client.verify.services(app.config['TWILLO_VERUFY_SID'])
    verify.verifications.create(to=to, channel=channel)

def check_verification(phone, code):
    service = app.config.get("TWILIO_ACCOUNT_SID")
    
    try:
        verification_check = client.verify \
            .services(service) \
            .verification_checks \
            .create(to=phone, code=code)

        if verification_check.status == "approved":
            return True
        else:
            return False
    except Exception as e:
        return False

    return False

import AutoserviceAPI.mobile_authorization
import AutoserviceAPI.mobile_info