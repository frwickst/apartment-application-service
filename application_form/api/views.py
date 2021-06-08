# from datetime import datetime
# from users.models import Profile
import logging
from django.conf import settings
from django.db import transaction
from rest_framework import status  # serializers,
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apartment.api.serializers import ApartmentSerializer
from apartment.models import Project  # Apartment,
from application_form.api.serializers import (
    ApplicantSerializer,
    ApplicationApartmentSerializer,
    ApplicationSerializer,
)
from application_form.models import Application  # , ApplicationApartment
from users.models import Profile

_logger = logging.getLogger(__name__)

settings.DJANGO_LOG_LEVEL = "DEBUG"
settings.LOG_LEVEL = "DEBUG"


class ApplicationViewSet(ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer

    @transaction.atomic
    def create(self, request):
        print(request)
        apartments_data = request.data.pop("apartments")
        project_uuid = request.data.pop("project_id")
        project, _ = Project.objects.get_or_create(id=project_uuid)
        additional_aplicant_data = request.data.pop("additional_applicant")

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
                apartment_data = {"id": apartment_id, "project": project.id}
                apartment_serializer = ApartmentSerializer(data=apartment_data)
                apartment_serializer.is_valid(raise_exception=True)
                apartment_created = apartment_serializer.create(
                    apartment_serializer.validated_data
                )
                _logger.info(f"apartments {apartment_created.pk} created")

                applicationapartment_data = {
                    "application": application.id,
                    "apartment": apartment_created.id,
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
            applicant = Profile.objects.get(id=request.data["user_id"])
            applicant_data = {
                "application": application.id,
                "first_name": applicant.user.first_name,
                "last_name": applicant.user.last_name,
                "email": applicant.user.email,
                "address": applicant.address,
                "postal_code": applicant.postal_code,
                "city": applicant.city,
                "phone_number": applicant.phone_number,
                "date_of_birth": applicant.date_of_birth.strftime("%Y-%m-%d"),
                # datetime.strptime(
                # applicant.date_of_birth, "%Y-%m-%d"
                # applicant.date_of_birth,  # .strftime("%Y-%m-%d"),
                "is_primary_applicant": True,
            }
            # print("------applicant", applicant.)
            applicant_serializer = ApplicantSerializer(data=applicant_data)
            applicant_serializer.is_valid(raise_exception=True)
            applicant = applicant_serializer.create(applicant_serializer.validated_data)
            _logger.info(f"applicant {applicant.pk} created")

            if additional_aplicant_data:
                additional_aplicant_data["application"] = application.id
                applicant_serializer = ApplicantSerializer(
                    data=additional_aplicant_data
                )
                applicant_serializer.is_valid(raise_exception=True)
                applicant = applicant_serializer.create(
                    applicant_serializer.validated_data
                )
            _logger.info(f"additional applicant {applicant.pk} created")
        except Exception:
            _logger.exception("Applicants not created")
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_201_CREATED)
