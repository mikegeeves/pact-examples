const axios = require("axios");
const { Bear } = require("./bear");

class BearApiClient {
  constructor(url) {
    this.url = url;
  }

  async getSpecies(name) {
    return axios
      .get(`${this.url}/species/${name}`)
      .then((r) => new Bear(r.data.name, r.data.colour));
  }
}
module.exports = {
  BearApiClient,
};
