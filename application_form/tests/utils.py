import datetime
import uuid

from apartment.tests.factories import IdentifierFactory
from application_form.tests.factories import ApplicantFactory


def haso_application_data_with_additional_applicant(profile):
    # build apartments by creating identifiers
    apartments = IdentifierFactory.build_batch_for_att_schema(5)
    apartments_data = {
        apartments.index(apartment): apartment.identifier for apartment in apartments
    }

    # build second applicant
    applicant = ApplicantFactory.build()

    # build application request data
    application_data = {
        "application_uuid": str(uuid.uuid4()),
        "application_type": "haso",
        "user_id": str(profile.id),
        "has_children": "True",
        "additional_applicant": {
            "first_name": applicant.first_name,
            "last_name": applicant.last_name,
            "email": applicant.email,
            "street_address": applicant.street_address,
            "postal_code": applicant.postal_code,
            "city": applicant.city,
            "phone_number": applicant.phone_number,
            "date_of_birth": datetime.datetime(2000, 5, 17),
        },
        "project_id": uuid.uuid4(),
        "apartments": apartments_data,
    }
    return application_data
