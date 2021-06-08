# from apartment.models import Apartment, Project
# from apartment.api.serializers import ApartmentSerializer
# from enumfields.drf.serializers import EnumSupportSerializerMixin
# from application_form.enums import ApplicationType
from datetime import datetime
from rest_framework import serializers
from rest_framework.fields import UUIDField

from application_form.models import Applicant, Application, ApplicationApartment
from users.models import Profile


class ApplicantSerializer(serializers.ModelSerializer):
    age = serializers.SerializerMethodField()

    class Meta:
        model = Applicant
        fields = "__all__"
        #  [
        #     "first_name",
        #     "last_name",
        #     "email",
        #     "street_address",
        #     "postal_code",
        #     "city",
        #     "phone_number",
        #     # "age",
        #  ]

    def get_age(self, obj):
        print("something")
        if obj.age:

            return obj.age
        # date = datetime.strptime(instance.date_of_birth.year)
        print("----", datetime.now().year - self.date_of_birth.year)
        return datetime.now().year - self.date_of_birth.year


class ApplicationSerializer(serializers.ModelSerializer):
    application_uuid = UUIDField(source="external_uuid", format="hex_verbose")
    additional_applicant = serializers.IntegerField(source="applicants_count")
    application_type = serializers.CharField(source="type")
    user_id = UUIDField(source="profile_id", format="hex_verbose")
    right_of_residence = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = [
            "application_uuid",
            "application_type",
            "additional_applicant",
            "user_id",
            "right_of_residence",
            "has_children",
        ]

    # def get_applicants_count(self):
    #     if self.additional_applicant:
    #         return 2
    #     return 1

    def get_profile(self):
        print("something")
        return Profile.objects.get(id=self.user_id)

    def get_right_of_residence(self, obj):
        if obj.right_of_residence:
            return obj.right_of_residence
        return Profile.objects.get(id=self.user_id).right_of_residence


class ApplicationApartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationApartment
        fields = "__all__"
