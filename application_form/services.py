import logging
from elasticsearch_dsl import Search

from connections.utils import create_elastic_connection

_logger = logging.getLogger(__name__)
create_elastic_connection()


class ApplicationFormService(object):
    def __init__(self, request):
        self.request = request

    def get_elastic_apartment_data(self, identifier):
        """
        Fetch apartments for sale from elasticsearch and map them for Oikotie
        """
        s_obj = Search().query("match", uuid=identifier)
        s_obj.execute()
        scan = list(s_obj.scan())

        if len(scan) > 1 or len(scan) < 1:
            _logger.error(
                f"There were problems fetching apartment elastic data."
                f"There were {len(scan)} apartments with uuid {identifier}"
            )
            exit(1)

        street_address = scan[0].project_street_address
        apartment_number = scan[0].apartment_number

        _logger.debud(f"Succefully fetched data for apartment {identifier}")
        return street_address, apartment_number

    def get_elastic_project_data(self, identifier):
        """
        Fetch apartments for sale from elasticsearch and map them for Oikotie
        """
        s_obj = Search().query("match", project_uuid=identifier)
        s_obj.execute()
        scan = list(s_obj.scan())

        if len(scan) < 1:
            _logger.error(f"There were no apartments with project uuid {identifier}")
            exit(1)

        street_address = scan[0].project_street_address

        _logger.debud(f"Succefully fetched data for apartment {identifier}")
        return street_address
