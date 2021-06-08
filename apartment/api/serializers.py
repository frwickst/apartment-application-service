from rest_framework import serializers

from apartment.models import Apartment, Identifier, Project


class IdentifierSerializer(serializers.ModelSerializer):
    # schema_type = serializers.CharField(IdentifierSchemaType)

    class Meta:
        model = Identifier
        fields = "__all__"


class ProjectSerializer(serializers.ModelSerializer):
    street_address = serializers.SerializerMethodField(allow_null=False)
    identifiers = IdentifierSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = "__all__"

    def get_street_address(self):
        return "elastic_apartment_street_address"


class ApartmentSerializer(serializers.ModelSerializer):
    street_address = serializers.SerializerMethodField()
    apartment_number = serializers.SerializerMethodField()  # serializers.IntegerField()
    identifiers = IdentifierSerializer(many=True, read_only=True)

    class Meta:
        model = Apartment
        fields = ["street_address", "apartment_number", "identifiers", "project"]
        # "__all__"

    def get_street_address(self):
        # print("returning street")
        return "elastic_apartment_street_address"

    def get_apartment_number(self):
        return 1
