import logging
from django.db import transaction
from rest_framework import serializers

from apartment.models import Apartment, Identifier, Project

_logger = logging.getLogger(__name__)


class IdentifierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Identifier
        fields = "__all__"


class ProjectSerializer(serializers.ModelSerializer):
    identifier = serializers.CharField(allow_null=False)
    schema_type = serializers.CharField(allow_null=False)

    class Meta:
        model = Project
        fields = [
            "schema_type",
            "identifier",
            "street_address",
        ]

    @transaction.atomic
    def create(self, validated_data):
        project = Project.objects.create(
            street_address=validated_data["street_address"],
        )
        Identifier.objects.create(
            schema_type=validated_data["schema_type"],
            identifier=validated_data["identifier"],
            project=project,
        )
        return project


class ApartmentSerializer(serializers.ModelSerializer):
    identifier = serializers.CharField(allow_null=False)
    schema_type = serializers.CharField(allow_null=False)

    class Meta:
        model = Apartment
        fields = [
            "street_address",
            "apartment_number",
            "schema_type",
            "identifier",
            "project",
        ]
        # "__all__"

    @transaction.atomic
    def create(self, validated_data):
        apartment = Apartment.objects.create(
            street_address=validated_data["street_address"],
            apartment_number=validated_data["apartment_number"],
            project=validated_data["project"],
        )
        Identifier.objects.create(
            schema_type=validated_data["schema_type"],
            identifier=validated_data["identifier"],
            apartment=apartment,
        )
        return apartment
