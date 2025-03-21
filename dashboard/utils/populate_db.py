import os
import django
import random
from faker import Faker

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'neft.settings')
django.setup()

from dashboard.models import Brigade, Category, Document, Equipment
from django.contrib.auth.models import User, Group

fake = Faker('ru_RU')


def populate_brigades(num_brigades=5):
    """Создает бригады."""
    for _ in range(num_brigades):
        try:
            b = Brigade.objects.create(name=fake.unique.company(), description=fake.text(max_nb_chars=200))
            print(b)
        except Exception as e:
            pass
    print("Бригады успешно созданы.")


def populate_categories(num_categories=5, with_subcategories=True):
    """Создает категории и подкатегории."""

    categories = []
    for _ in range(num_categories):
        try:
            c = category = Category.objects.create(name=fake.unique.job(), description=fake.text(max_nb_chars=200))
            print(c)
            categories.append(category)
        except Exception as e:
            pass

    if with_subcategories:
        for category in categories:
            for _ in range(random.randint(0, 3)):
                try:
                    c = Category.objects.create(name=fake.unique.job(), description=fake.text(max_nb_chars=200), parent=category)
                    print(c)
                except Exception as e:
                    pass
    print("Категории успешно созданы.")


def populate_documents(num_documents=10):
    """Создаёт документы."""
    for _ in range(num_documents):
        d = Document.objects.create(title=fake.text(max_nb_chars=50), file=fake.file_path(depth=1))
        print(d)
    print("Документы успешно созданы.")


def populate_equipment(num_equipment=50):
    """Создаёт оборудование"""
    brigades = list(Brigade.objects.all())
    categories = list(Category.objects.all())
    documents = list(Document.objects.all())

    for _ in range(num_equipment):
        e = equipment = Equipment.objects.create(
            serial=fake.unique.bothify(text='????-#######'),
            name=fake.unique.text(max_nb_chars=50),
            category=random.choice(categories),
            brigade=random.choice(brigades) if brigades else None,
            date_release=fake.date_between(start_date='-10y', end_date='today'),
            date_exploitation=fake.date_between(start_date='-5y', end_date='today'),
            condition=random.choice(['work', 'faulty', 'repair'])
        )
        equipment.documents.set(random.sample(documents, random.randint(0, min(len(documents), 5))))
        print(e)
    print("Оборудование успешно создано")


def populate_users(num_users=5):
    """Создаёт пользователей."""
    for i in range(num_users):
        try:
            username = fake.unique.user_name()
            u = User.objects.create_user(
                username=username,
                password='password',
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.email(),
                is_staff=fake.boolean(),
                is_superuser=False
            )
            print(u)
            if fake.boolean():
                user = User.objects.get(username=username)
                user.groups.add(random.choice(list(Group.objects.all())))
        except Exception as e:
            pass
    admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'password')
    print("Пользователи и админ успешно созданы")


def run():
    populate_brigades(25)
    populate_categories(10)
    populate_documents(50)
    populate_equipment(300)
    populate_users(15)


if __name__ == '__main__':
    run()
    print("Заполнение базы данных успешно завершено.")
