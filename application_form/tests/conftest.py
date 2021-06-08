import faker.config
from pytest import fixture
from rest_framework.test import APIClient

faker.config.DEFAULT_LOCALE = "fi_FI"


@fixture(scope="session")
def api_client():
    api_client = APIClient()
    return api_client
