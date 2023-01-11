// Pact annotated code block - Setting up the Consumer
const { pactWith } = require("jest-pact");
const { BearConsumer } = require("../../src/consumer");

pactWith(
  {
    consumer: "BearServiceClient",
    provider: "BearService",
    dir: "./output/pacts",
  },
  (provider) => {
    let client;

    beforeEach(() => {
      client = new BearConsumer(provider.mockService.baseUrl);
    });
    // End Pact annotated code block

    //  Pact annotated code block - Defining the pact, and calling the consumer
    describe("Test Bear species endpoint", () => {
      const expectedResponse = {
        name: "Polar",
        colour: "White",
      };
      beforeEach(() =>
        provider.addInteraction({
          state: "There are some bears",
          uponReceiving: "A request for the Polar bear species by name",
          withRequest: {
            method: "GET",
            path: "/species",
            query: { name: "Polar" },
          },
          willRespondWith: {
            status: 200,
            body: expectedResponse,
          },
        })
      );

      it("returns a bear", () => {
        return client.getSpecies("Polar").then((resp) => {
          expect(resp).toEqual(expectedResponse);
        });
      });
    });
    //  End Pact annotated code block
  }
);
