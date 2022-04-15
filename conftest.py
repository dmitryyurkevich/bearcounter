import pytest

from client import Client
from service import Service


@pytest.fixture(scope="function")
def service():
    image = "azshoo/alaska"
    exposed_port = 8091
    with Service(image=image, exposed_port=exposed_port) as service:
        yield service


@pytest.fixture(scope="function")
def client(service):
    with Client(service=service) as client:
        yield client


