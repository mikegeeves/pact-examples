const axios = require("axios");
const { BearSpecies } = require("./bear-species");

class BearApiClient {
  constructor(url) {
    this.url = url;
  }

  async getSpecies(id) {
    return axios
      .get(`${this.url}/species/${id}`)
      .then((r) => new BearSpecies(r.data.name, r.data.colour));
  }
}
module.exports = {
  BearApiClient,
};
