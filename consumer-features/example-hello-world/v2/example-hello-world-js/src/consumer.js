// import axios from "axios";

const axios = require("axios");

const defaultBaseUrl = "http://your-api.example.com";

const api = (baseUrl = defaultBaseUrl) => ({
  getSpecies: (name) =>
    axios.get(`${baseUrl}/species/` + name).then((response) => {
      return Bear(response.data.name, response.data.colour);
    }),
});

const Bear = (name, colour) => {
  return {
    name,
    colour,
  };
};

module.exports = {
  api,
  Bear,
};
