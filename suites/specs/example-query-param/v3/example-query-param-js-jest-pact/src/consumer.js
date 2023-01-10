const axios = require("axios");
const { BearSpecies } = require("./bear-species");

class BearConsumer {
  constructor(url) {
    this.url = url;
  }

  async getSpecies(name) {
    return axios
      .get(`${this.url}/species?name=${name}`)
      .then((r) => new BearSpecies(r.data.name, r.data.colour));
  }
}
module.exports = {
  BearConsumer,
};
