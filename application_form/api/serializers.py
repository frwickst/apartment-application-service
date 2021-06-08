from rest_framework import serializers
from rest_framework.fields import UUIDField

from application_form.models import Applicant, Application, ApplicationApartment
from users.models import Profile


class ApplicantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applicant
        fields = "__all__"


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

    def get_right_of_residence(self, obj):
        if obj.right_of_residence:
            return obj.right_of_residence
        return Profile.objects.get(id=self.user_id).right_of_residence


class ApplicationApartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationApartment
        fields = "__all__"
