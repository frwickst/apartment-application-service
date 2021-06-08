import pytest
import uuid
from django.conf import settings

from apartment.models import Apartment, Project
from application_form.models import Applicant, Application, ApplicationApartment
from application_form.tests.factories import (  # ApplicantFactory,
    ApplicationWithApplicantsFactory,
)
from application_form.tests.utils import haso_application_data_with_additional_applicant
from users.tests.factories import ProfileFactory

# from users.models import Profile, User

settings.DJANGO_LOG_LEVEL = "DEBUG"
settings.LOG_LEVEL = "DEBUG"


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


@pytest.mark.django_db
def test_application_post(client):
    profile_uuid = uuid.uuid4()
    profile = ProfileFactory(id=profile_uuid)
    data = haso_application_data_with_additional_applicant(profile)

    response = client.post("/v1/applications/", data, content_type="application/json")
    print(
        "---test",
        Application.objects.get(external_uuid=data["application_uuid"]).profile,
    )
    assert response.status_code == 201
    assert Project.objects.first().identifiers
    assert Application.objects.get(external_uuid=data["application_uuid"]).profile
    assert Apartment.objects.filter(project=Project.objects.first()).count() == 5
    assert (
        ApplicationApartment.objects.filter(
            application__pk=data["application_uuid"]
        ).count()
        == 5
    )
    assert Applicant.objects.get(pk=data["user_id"])
    assert Applicant.objects.get(
        first_name=data["additional_applicant"]["first_name"],
        last_name=data["additional_applicant"]["last_name"],
    )
    assert False
