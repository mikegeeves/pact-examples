"""pact test for Bear service client"""

import atexit
import logging
import os

import pytest
from pact import Consumer, Provider

from consumer import BearConsumer

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Define where to run the mock server, for the consumer to connect to. These
# are the defaults so may be omitted
PACT_MOCK_HOST = "localhost"
PACT_MOCK_PORT = 1234

# Where to output the JSON Pact files created by any tests
# This is optional, but means we can keep it tidier than everything going in together
PACT_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "output", "pacts")

# Where to output the pact-mock-service.log to
# This is optional, but means we can keep it tidier than everything going in together
LOG_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "output", "logs")


@pytest.fixture
def consumer() -> BearConsumer:
    return BearConsumer("http://{host}:{port}".format(host=PACT_MOCK_HOST, port=PACT_MOCK_PORT))


@pytest.fixture(scope="session")
def mock_provider(request):
    """Setup a Pact Consumer, which provides the Provider mock service and generates the Pacts"""

    # Pact annotated code block - Setting up the mock Provider
    # (1) Configure our Pact mock Provider
    mock_provider = Consumer("BearServiceClient").has_pact_with(
        Provider("BearService"),
        host_name=PACT_MOCK_HOST,
        port=PACT_MOCK_PORT,
        pact_dir=PACT_DIR,
        log_dir=LOG_DIR,
    )
    # End Pact annotated code block

    mock_provider.start_service()

    # Make sure the Pact mocked provider is stopped when we finish, otherwise
    # port 1234 may become blocked
    atexit.register(mock_provider.stop_service)

    yield mock_provider

    # This will stop the Pact mock server.
    # If we were publishing Pacts to the broker, they would now be submitted
    mock_provider.stop_service()

    # Given we have cleanly stopped the service, we do not want to re-submit the
    # Pacts to the Pact Broker again atexit, since the Broker may no longer be
    # available if it has been started using the --run-broker option, as it will
    # have been torn down at that point
    mock_provider.publish_to_broker = False


def test_get_polar_bear(mock_provider, consumer):
    # Define the Matcher; the expected structure and content of the response
    # In this case we are searching for the specific response, in most cases you
    # will need to use matchers to allow different values within some constraints.
    expected = {
        "name": "Polar",
        "colour": "White",
    }

    # Define the expected behaviour of the Provider. This determines how the
    # Pact mock provider will behave. In this case, we expect a body which is
    # "Like" the structure defined above. This means the mock provider will
    # return the EXACT content where defined, e.g. UserA for name, and SOME
    # appropriate content e.g. for ip_address.

    # Pact annotated code block - Defining the pact, and calling the consumer
    # Arrange: declare our expected interactions
    (
        mock_provider.given("There are some bears")
        .upon_receiving("A request for the Bear species with id 1")
        .with_request("GET", "/species/1")
        .will_respond_with(200, body=expected)
    )

    with mock_provider:
        # Act: make the Consumer interact with the mock Provider
        species = consumer.get_species(1)

        # Assert: check the result is as expected
        # In this case the mock Provider will have returned a valid response
        assert species.name == "Polar"
        assert species.colour == "White"

        # Make sure that all interactions defined occurred
        mock_provider.verify()
    # End Pact annotated code block
