# from apartment.models import Apartment, Project
# from apartment.api.serializers import ApartmentSerializer
# from enumfields.drf.serializers import EnumSupportSerializerMixin
# from application_form.enums import ApplicationType
from datetime import datetime
from rest_framework import serializers
from rest_framework.fields import CharField, UUIDField  # ChoiceField, IntegerField,

from application_form.models import Applicant, Application, ApplicationApartment
from users.models import Profile


class ApplicantSerializer(serializers.ModelSerializer):
    date_of_birth = serializers.CharField(source="age")

    class Meta:
        model = Applicant
        fields = [
            "first_name",
            "last_name",
            "email",
            "address",
            "postal_code",
            "city",
            "phone_number",
            "date_of_birth",
        ]

    def get_age(self, instance):
        # date = datetime.strptime(instance.date_of_birth.year)
        print("----", datetime.now().year - instance.date_of_birth.year)
        return datetime.now().year - instance.date_of_birth.year


class ApplicationSerializer(serializers.ModelSerializer):
    application_uuid = UUIDField(source="id", format="hex_verbose")
    application_type = CharField(source="type")
    applicants_count = serializers.SerializerMethodField()
    user_id = UUIDField(source="profile_id", format="hex_verbose")

    class Meta:
        model = Application
        fields = [
            "application_uuid",
            "application_type",
            "applicants_count",
            "user_id",
            "has_children",
        ]

    def get_applicants_count(self, instance):
        if instance.additional_aplicant_data:
            return 2
        return 1

    def get_profile(self, instance):
        return Profile.objects.get(id=instance.user_id)


class ApplicationApartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationApartment
        fields = "__all__"
