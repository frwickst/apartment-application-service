import pytest
import uuid
from django.conf import settings

from apartment.models import Apartment, Project
from application_form.models import Applicant, Application, ApplicationApartment
from application_form.tests.factories import ApplicationWithApplicantsFactory
from application_form.tests.utils import haso_application_data_with_additional_applicant
from connections.utils import create_elastic_connection
from users.models import Profile
from users.tests.factories import ProfileFactory

settings.DJANGO_LOG_LEVEL = "DEBUG"
settings.LOG_LEVEL = "DEBUG"
create_elastic_connection()


@pytest.mark.django_db
def test_application_get_detail(client):
    application_uuid = uuid.uuid4()
    application = ApplicationWithApplicantsFactory.create(
        external_uuid=application_uuid
    )
    # print(Application.objects.get(external_uuid=application_uuid))
    response = client.get(f"/v1/applications/{application_uuid}", follow=True)

    assert response.status_code == 200
    assert response.data["application_uuid"] == str(application.external_uuid)


@pytest.mark.django_db
def test_application_get_list(client):
    ApplicationWithApplicantsFactory.create_batch(5)
    response = client.get("/v1/applications/")

    assert response.status_code == 200
    assert len(response.data) == 5


@pytest.mark.usefixtures("elastic_apartments")
@pytest.mark.django_db
def test_application_post(client, elastic_apartments):
    print("----------------", elastic_apartments)
    profile_uuid = uuid.uuid4()
    profile = ProfileFactory(id=profile_uuid)
    data = haso_application_data_with_additional_applicant(profile)
    print(data)
    response = client.post("/v1/applications/", data, content_type="application/json")

    assert response.status_code == 201
    assert Project.objects.first().identifiers
    assert Application.objects.get(external_uuid=data["application_uuid"]).profile
    assert Apartment.objects.filter(project=Project.objects.first()).count() == 5

    expected_applicationapartments = ApplicationApartment.objects.filter(
        application__pk=Application.objects.get(
            external_uuid=data["application_uuid"]
        ).pk
    )
    assert expected_applicationapartments.count() == 5

    existing_application = Application.objects.get(
        external_uuid=data["application_uuid"]
    )
    expected_applicant = Applicant.objects.get(
        first_name=Profile.objects.get(id=data["user_id"]).user.first_name,
        last_name=Profile.objects.get(id=data["user_id"]).user.last_name,
        street_address=Profile.objects.get(id=data["user_id"]).street_address,
    )
    assert expected_applicant.application == existing_application

    expected_additional_applicant = Applicant.objects.get(
        first_name=data["additional_applicant"]["first_name"],
        last_name=data["additional_applicant"]["last_name"],
    )
    assert expected_additional_applicant.application == existing_application
