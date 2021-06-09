import logging
import uuid
from elasticsearch_dsl import Search

from apartment.tests.factories import IdentifierFactory
from application_form.tests.factories import ApplicantFactory
from connections.enums import ApartmentStateOfSale
from connections.utils import create_elastic_connection

_logger = logging.getLogger(__name__)
create_elastic_connection()


def get_elastic_apartments_uuids() -> list:
    s_obj = (
        Search()
        .query("match", _language="fi")
        .query("match", apartment_state_of_sale=ApartmentStateOfSale.FOR_SALE)
    )
    s_obj.execute()
    scan = s_obj.scan()
    uuids = []
    project_uuid = ""
    while len(uuids) <= 5:
        for hit in scan:
            uuids.append(str(hit.uuid))
            project_uuid = str(hit.project_uuid)
    return project_uuid, uuids


def haso_application_data_with_additional_applicant(profile):
    # build apartments by creating identifiers
    project_uuid, apartment_uuids = get_elastic_apartments_uuids()
    # print("----------------", elastic_apartments)
    apartments = IdentifierFactory.build_batch_for_att_schema(5, apartment_uuids)
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
        "has_children": True,
        "additional_applicant": {
            "first_name": applicant.first_name,
            "last_name": applicant.last_name,
            "email": applicant.email,
            "street_address": applicant.street_address,
            "postal_code": applicant.postal_code,
            "city": applicant.city,
            "phone_number": applicant.phone_number,
            "date_of_birth": "2000-05-14",
        },
        "project_id": project_uuid,
        "apartments": apartments_data,
    }
    return application_data
