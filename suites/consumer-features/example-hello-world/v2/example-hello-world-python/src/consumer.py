from typing import Optional

import requests


class BearSpecies(object):
    """Define the basic BearSpecies data we expect to receive from the Bear Provider."""

    def __init__(self, name: str, colour: str):
        self.name = name
        self.colour = colour


class BearConsumer(object):
    """Demonstrate some basic functionality of how the Bear Consumer will interact
    with the Bear Provider, in this case a simple get_species."""

    def __init__(self, base_url: str):
        """Initialise the Consumer, in this case we only need to know the URI.

        :param base_url: The full URL, including port of the Provider to connect to
        """
        self.base_url = base_url

    def get_species(self, species_id: int) -> Optional[BearSpecies]:
        """Fetch a Bear Species object by id from the server.

        :param species_id: Species id to search for
        :return: The BearSpecies requested if found, None if not found
        """
        url = f"{self.base_url}/species/{species_id}"
        response = requests.get(url)
        print(response.json())
        if response.status_code == 404:
            return None

        name = response.json()["name"]
        colour = response.json()["colour"]

        return BearSpecies(name, colour)
