import logging
from datetime import datetime
from django.conf import settings
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apartment.api.serializers import ApartmentSerializer, ProjectSerializer
from apartment.enums import IdentifierSchemaType
from application_form.api.serializers import (
    ApplicantSerializer,
    ApplicationApartmentSerializer,
    ApplicationSerializer,
)
from application_form.models import Application
from users.models import Profile

_logger = logging.getLogger(__name__)

settings.DJANGO_LOG_LEVEL = "DEBUG"
settings.LOG_LEVEL = "DEBUG"


class ApplicationViewSet(ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    lookup_field = "external_uuid"

    @transaction.atomic
    def create(self, request):  # noqa: C901
        # print("----request.data----", request.data)
        project_uuid = request.data.pop("project_id")
        project_data = {
            "schema_type": "att_pro_es",
            "identifier": str(project_uuid),
            "street_address": "some address",
        }
        try:
            project_serializer = ProjectSerializer(data=project_data)
            project_serializer.is_valid(raise_exception=True)
            project = project_serializer.create(project_serializer.validated_data)
            _logger.info(f"Project {project.pk} created")
        except Exception:
            _logger.exception(f"Project {project_uuid} not created")
            return Response(status=status.HTTP_400_BAD_REQUEST)

        apartments_data = request.data.pop("apartments")
        additional_applicant_data = request.data["additional_applicant"]
        if additional_applicant_data:
            request.data["additional_applicant"] = 2

        try:
            application_serializer = self.get_serializer(data=request.data)
            application_serializer.is_valid(raise_exception=True)
            application = application_serializer.create(
                application_serializer.validated_data
            )

            _logger.info(f"Application {application.pk} created")
        except Exception:
            _logger.exception(
                f"Application {request.data['application_uuid']} not \
created"
            )
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            for priority, apartment_id in apartments_data.items():
                apartment_data = {
                    "schema_type": IdentifierSchemaType("att_pro_es"),
                    "identifier": apartment_id,
                    "street_address": "something",
                    "apartment_number": 1,
                    "project": project.id,
                }
                apartment_serializer = ApartmentSerializer(data=apartment_data)
                apartment_serializer.is_valid(raise_exception=True)
                apartment_created = apartment_serializer.create(
                    apartment_serializer.validated_data
                )
                _logger.info(f"apartments {apartment_created.pk} created")

                applicationapartment_data = {
                    "application": application.pk,
                    "apartment": apartment_created.pk,
                    "priority_number": priority,
                }
                applicationapartment_serializer = ApplicationApartmentSerializer(
                    data=applicationapartment_data
                )
                applicationapartment_serializer.is_valid(raise_exception=True)
                applicationapartment = applicationapartment_serializer.create(
                    applicationapartment_serializer.validated_data
                )
                _logger.info(f"apartments {applicationapartment.pk} created")
        except Exception:
            _logger.exception("Apartment not created")
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            # primary applicant
            applicant = Profile.objects.get(id=request.data["user_id"])
            applicant_age = datetime.now().year - applicant.date_of_birth.year
            applicant_data = {
                "application": application.id,
                "first_name": applicant.user.first_name,
                "last_name": applicant.user.last_name,
                "email": applicant.user.email,
                "street_address": applicant.street_address,
                "postal_code": applicant.postal_code,
                "city": applicant.city,
                "phone_number": applicant.phone_number,
                "age": applicant_age,
                "is_primary_applicant": True,
            }

            applicant_serializer = ApplicantSerializer(data=applicant_data)
            applicant_serializer.is_valid(raise_exception=True)
            print("---applicant_data", applicant_serializer.validated_data)
            applicant = applicant_serializer.create(applicant_serializer.validated_data)
            _logger.info(f"Primary applicant {applicant.pk} created")
        except Exception:
            _logger.exception(f"Primary applicant {applicant.pk} not created")
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # try:
        #     # additional applicant
        #     if additional_applicant_data:
        #         additional_applicant_data["application"] = application.id
        #         applicant_age = datetime.now().year - applicant.date_of_birth.year
        #         applicant_serializer = ApplicantSerializer(
        #             data=additional_applicant_data
        #         )
        #         applicant_serializer.is_valid(raise_exception=True)
        #         applicant = applicant_serializer.create(
        #             applicant_serializer.validated_data
        #         )
        #     _logger.info(f"Additional applicant {applicant.pk} created")
        # except Exception:
        #     _logger.exception("Additional applicant not created")
        #     return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_201_CREATED)
