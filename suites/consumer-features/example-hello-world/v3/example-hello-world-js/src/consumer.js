const axios = require("axios");
const { BearSpecies } = require("./bear-species");

/** Demonstrate some basic functionality of how the Bear Consumer will interact with the Bear Provider, in this case a simple getSpecies. */
class BearConsumer {
  /**
   * Initialise the Consumer, in this case we only need to know the URI.
   *
   * @param {str} base_url - The full URI, including port of the Provider to connect to.
   */
  constructor(baseUrl) {
    this.baseUrl = baseUrl;
  }

  /**
   * Fetch a Bear Species object by id from the server.
   *
   * @param {int} species_id - Species id to search for
   * @return {BearSpecies} The BearSpecies requested
   */
  async getSpecies(id) {
    return axios
      .get(`${this.baseUrl}/species/${id}`)
      .then((r) => new BearSpecies(r.data.name, r.data.colour));
  }
}

module.exports = {
  BearConsumer,
};
