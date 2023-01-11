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

    describe("Test Bear species endpoint", () => {
      const expectedResponse = {
        name: "Polar",
        colour: "White",
      };
      beforeEach(
        () =>
          //  Pact annotated code block - Interaction
          provider.addInteraction({
            state: "There are some bears",
            uponReceiving: "A request for the Polar bear species by name",
            withRequest: {
              method: "GET",
              path: "/species",
              // highlight-next-line
              query: { name: "Polar" },
            },
            willRespondWith: {
              status: 200,
              body: expectedResponse,
            },
          })
        // End Pact annotated code block
      );

      it("returns a bear", () => {
        return client.getSpecies("Polar").then((resp) => {
          expect(resp).toEqual(expectedResponse);
        });
      });
    });
  }
);
