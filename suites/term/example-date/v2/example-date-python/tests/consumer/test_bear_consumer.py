"""pact test for Bear service client"""

import atexit
import logging
import os

import pytest
from pact import Consumer, Provider, Format

from consumer import BearConsumer

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

PACT_MOCK_HOST = "localhost"
PACT_MOCK_PORT = 1234

PACT_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "output", "pacts")
LOG_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "output", "logs")


@pytest.fixture
def consumer() -> BearConsumer:
    return BearConsumer("http://{host}:{port}".format(host=PACT_MOCK_HOST, port=PACT_MOCK_PORT))


@pytest.fixture(scope="session")
def pact(request):
    # Pact annotated code block - Setting up the Consumer
    pact = Consumer("BearServiceClient").has_pact_with(
        Provider("BearService"),
        host_name=PACT_MOCK_HOST,
        port=PACT_MOCK_PORT,
        pact_dir=PACT_DIR,
        log_dir=LOG_DIR,
    )
    # End Pact annotated code block

    pact.start_service()
    atexit.register(pact.stop_service)
    yield pact

    pact.stop_service()
    pact.publish_to_broker = False


def test_get_polar_bear_birthday(pact, consumer):
    expected = {
        "birthday": Format().date,
    }

    # Pact annotated code block - Defining the pact, and calling the consumer
    (
        pact.given("There are some bears")
        .upon_receiving("A request for the first Bear's birthday")
        .with_request("GET", "/bear/1/birthday")
        .will_respond_with(200, body=expected)
    )

    with pact:
        # Perform the actual request
        species = consumer.get_birthday("Polar")

        # In this case the mock Provider will have returned a valid response
        assert species.birthday == "2010-07-19"

        # Make sure that all interactions defined occurred
        pact.verify()
    # End Pact annotated code block
