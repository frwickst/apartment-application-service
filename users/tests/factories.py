import factory
import string
from factory import Faker, fuzzy

from users.models import Profile, User

CONTACT_LANGUAGE_CHOICES = ["fi", "sv", "en"]


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    first_name = Faker("first_name")
    last_name = Faker("last_name")
    email = Faker("email")


class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Profile

    id = factory.Faker("uuid4")
    phone_number = Faker("phone_number")
    street_address = Faker("street_address")
    city = Faker("city")
    postal_code = Faker("postcode")
    date_of_birth = Faker("date_of_birth", minimum_age=18, maximum_age=99)
    right_of_residence = fuzzy.FuzzyText(length=10, chars=string.digits)
    contact_language = fuzzy.FuzzyChoice(list(CONTACT_LANGUAGE_CHOICES))
    user = factory.SubFactory(UserFactory)
