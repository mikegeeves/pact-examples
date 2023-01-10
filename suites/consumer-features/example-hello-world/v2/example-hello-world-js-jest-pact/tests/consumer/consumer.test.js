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
          uponReceiving: "A request for the Bear species with id 1",
          withRequest: {
            method: "GET",
            path: "/species/1",
          },
          willRespondWith: {
            status: 200,
            body: expectedResponse,
          },
        })
      );

      it("Returns a Bear species", () => {
        return client.getSpecies(1).then((resp) => {
          expect(resp).toEqual(expectedResponse);
        });
      });
    });
    //  End Pact annotated code block
  }
);
