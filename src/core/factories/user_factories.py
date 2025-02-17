import factory
from faker import Faker

from api.users.utils import bcrypt_context
from core.database.models import User

fake = Faker()


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = None

    username = factory.LazyAttribute(lambda _: fake.user_name())
    first_name = factory.LazyAttribute(lambda _: fake.first_name())
    last_name = factory.LazyAttribute(lambda _: fake.last_name())
    email = factory.LazyAttribute(lambda _: fake.email())
    password = factory.LazyAttribute(lambda _: bcrypt_context.hash("password123"))
    is_teacher = False
    is_active = True
    is_superuser = False
