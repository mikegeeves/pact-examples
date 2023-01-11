const { pactWith } = require("jest-pact/dist/v3");
const { BearConsumer } = require("../../src/consumer");

pactWith(
  {
    consumer: "BearServiceClient",
    provider: "BearService",
    dir: "./output/pacts",
  },
  (interaction) => {
    interaction("Test Bear species endpoint", ({ provider, execute }) => {
      const expectedResponse = {
        name: "Polar",
        colour: "White",
      };

      beforeEach(
        () =>
          // Pact annotated code block - Interaction
          provider
            .given("There are some bears")
            .uponReceiving("A request for the Polar bear species by name")
            .withRequest({
              method: "GET",
              path: "/species",
              // highlight-next-line
              query: { name: "Polar" },
            })
            .willRespondWith({
              status: 200,
              body: { ...expectedResponse },
            })
        // End Pact annotated code block
      );

      execute("Returns a bear species", (mockserver) =>
        new BearConsumer(mockserver.url).getSpecies("Polar").then((resp) => {
          expect(resp).toEqual(expectedResponse);
        })
      );
    });
  }
);
