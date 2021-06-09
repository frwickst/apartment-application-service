import factory
from factory import Faker, fuzzy

from apartment.enums import IdentifierSchemaType
from apartment.models import Apartment, Identifier, Project


class ProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Project

    street_address = Faker("street_address")

    @factory.post_generation
    def identifiers(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for identifier in extracted:
                identifier = IdentifierFactory.create(
                    identifier=identifier[0],
                    schema_type=identifier[1],
                    apartment=None,
                    project=self,
                )
        else:
            identifier = IdentifierFactory.create(project=self, apartment=None)

        self.identifiers.add(identifier)


class ApartmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Apartment

    street_address = Faker("street_address")
    apartment_number = fuzzy.FuzzyInteger(0, 999)
    project = factory.SubFactory(ProjectFactory)

    @factory.post_generation
    def identifiers(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for identifier in extracted:
                identifier = IdentifierFactory.create(
                    identifier=identifier[0],
                    schema_type=identifier[1],
                    apartment=self,
                    project=None,
                )
        else:
            identifier = IdentifierFactory.create(apartment=self, project=None)
        self.identifiers.add(identifier)


class IdentifierFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Identifier
        django_get_or_create = ("identifier",)

    schema_type = fuzzy.FuzzyChoice(list(IdentifierSchemaType))
    identifier = fuzzy.FuzzyText(length=36)
    project = factory.SubFactory(ProjectFactory)
    apartment = factory.SubFactory(ApartmentFactory)

    @classmethod
    def build_batch_for_att_schema(cls, size: int, uuids_list: list):
        if not list:
            return [
                cls.build(
                    identifier=Faker("uuid4"),
                    schema_type=IdentifierSchemaType.ATT_PROJECT_ES,
                )
                for i in range(size)
            ]
        else:
            return [
                cls.build(
                    identifier=uuids_list[i],
                    schema_type=IdentifierSchemaType.ATT_PROJECT_ES,
                )
                for i in range(size)
            ]
