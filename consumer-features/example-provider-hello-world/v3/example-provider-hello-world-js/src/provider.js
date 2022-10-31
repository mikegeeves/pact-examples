const express = require("express");
const cors = require("cors");

const server = express();
server.use(cors());
server.use((req, res, next) => {
  res.header("Content-Type", "application/json; charset=utf-8");
  next();
});

server.get("/species/:name", (req, res) => {
  res.json({ name: "Polar", colour: "White" });
});

module.exports = {
  server,
};
