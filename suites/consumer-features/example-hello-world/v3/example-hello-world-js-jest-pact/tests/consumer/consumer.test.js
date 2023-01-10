// Pact annotated code block - Setting up the Consumer
const { pactWith } = require("jest-pact/dist/v3");
const { BearConsumer } = require("../../src/consumer");

// Pact annotated code block - Setting up the Consumer
pactWith(
  {
    consumer: "BearServiceClient",
    provider: "BearService",
    dir: "./output/pacts",
  },
  // End Pact annotated code block
  (interaction) => {
    interaction("Test Bear species endpoint", ({ provider, execute }) => {
      //  Pact annotated code block - Defining the pact, and calling the consumer

      const expectedResponse = {
        name: "Polar",
        colour: "White",
      };

      beforeEach(() =>
        provider
          .given("There are some bears")
          .uponReceiving("A request for the Bear species with id 1")
          .withRequest({
            method: "GET",
            path: "/species/1",
          })
          .willRespondWith({
            status: 200,
            body: { ...expectedResponse },
          })
      );

      execute("Returns a Bear species", (mockserver) =>
        new BearConsumer(mockserver.url).getSpecies(1).then((resp) => {
          expect(resp).toEqual(expectedResponse);
        })
      );
      //  End Pact annotated code block
    });
  }
);
