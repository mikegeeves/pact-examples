// Pact annotated code block - Setting up the Consumer
const { pactWith } = require("jest-pact/dist/v3");
const { BearApiClient } = require("../../src/consumer");

// Pact annotated code block - Setting up the Consumer
pactWith(
  {
    consumer: "BearServiceClient",
    provider: "BearService",
    dir: "./output/pacts",
  },
  // End Pact annotated code block
  (interaction) => {
    interaction("test bear endpoint", ({ provider, execute }) => {
      //  Pact annotated code block - Defining the pact, and calling the consumer

      const expectedResponse = {
        name: "Polar",
        colour: "White",
      };

      beforeEach(() =>
        provider
          .given("Some bears exist")
          .uponReceiving("a request for the Polar bear species")
          .withRequest({
            method: "GET",
            path: "/species/Polar",
          })
          .willRespondWith({
            status: 200,
            body: {
              status: 200,
              body: { ...expectedResponse },
            },
          })
      );

      execute("returns a bear", (mockserver) =>
        new BearApiClient(mockserver.url).getSpecies("Polar").then((resp) => {
          expect(resp).toEqual(expectedResponse);
        })
      );
      //  End Pact annotated code block
    });
  }
);
