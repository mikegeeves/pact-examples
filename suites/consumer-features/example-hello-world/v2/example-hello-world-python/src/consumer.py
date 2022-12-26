from typing import Optional

import requests


class BearSpecies(object):
    """Define the basic BearSpecies data we expect to receive from the Bear Provider."""

    def __init__(self, name: str, colour: str):
        self.name = name
        self.colour = colour


class BearConsumer(object):
    """Demonstrate some basic functionality of how the Bear Consumer will interact
    with the Bear Provider, in this case a simple get_bear."""

    def __init__(self, base_uri: str):
        """Initialise the Consumer, in this case we only need to know the URI.

        :param base_uri: The full URI, including port of the Provider to connect to
        """
        self.base_uri = base_uri

    def get_species(self, name: str) -> Optional[BearSpecies]:
        """Fetch a Bear object by species from the server.

        :param name: Species name to search for
        :return: BearSpecies details if found, None if not found
        """
        uri = self.base_uri + "/species/" + name
        response = requests.get(uri)
        print(response.json())
        if response.status_code == 404:
            return None

        name = response.json()["name"]
        colour = response.json()["colour"]

        return BearSpecies(name, colour)
