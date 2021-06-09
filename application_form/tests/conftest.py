import faker.config
import os
from elasticsearch.helpers.test import get_test_client, SkipTest
from elasticsearch_dsl.connections import add_connection
from pytest import fixture, skip
from rest_framework.test import APIClient
from time import sleep

from connections.tests.factories import ApartmentMinimalFactory

faker.config.DEFAULT_LOCALE = "fi_FI"


@fixture(scope="session")
def api_client():
    api_client = APIClient()
    return api_client


@fixture(autouse=True)
def use_test_elasticsearch_envs(settings):
    settings.ELASTICSEARCH_PORT = os.environ.get("ELASTICSEARCH_HOST_PORT", 9200)
    settings.ELASTICSEARCH_URL = os.environ.get("ELASTICSEARCH_HOST", "localhost")


@fixture()
def elastic_client():
    try:
        connection = get_test_client()
        add_connection("default", connection)
        yield connection
        connection.indices.delete("test-*", ignore=404)
    except SkipTest:
        skip()


@fixture()
def elastic_apartments():
    sale_apartments = []
    while len(sale_apartments) <= 5:
        elastic_apartments = ApartmentMinimalFactory.create_batch(20)
        sale_apartments = [
            item
            for item in elastic_apartments
            if item.apartment_state_of_sale == "FOR_SALE" and item._language == "fi"
        ]
    try:
        for item in elastic_apartments:
            item.save()
        sleep(3)
        yield elastic_apartments
    except SkipTest:
        skip()
