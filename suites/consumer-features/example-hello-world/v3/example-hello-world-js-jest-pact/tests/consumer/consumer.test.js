const { pactWith } = require("jest-pact/dist/v3");
const { BearConsumer } = require("../../src/consumer");

// Pact annotated code block - Setting up the mock Provider
// Configure our Pact mock Provider
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

      // Arrange: declare our expected interactions
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

      // Act: make the Consumer interact with the mock Provider
      execute("Returns a Bear species", (mockserver) =>
        new BearConsumer(mockserver.url).getSpecies(1).then((resp) => {
          // Assert: check the result is as expected
          expect(resp).toEqual(expectedResponse);
        })
      );
      //  End Pact annotated code block
    });
  }
);
