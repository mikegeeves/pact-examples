const { pactWith } = require("jest-pact");
const { BearConsumer } = require("../../src/consumer");

// Pact annotated code block - Setting up the mock Provider
// Configure our Pact mock Provider
pactWith(
  {
    consumer: "BearServiceClient",
    provider: "BearService",
    dir: "./output/pacts",
  },
  (mockProvider) => {
    // End Pact annotated code block
    let client;

    // Setup Pact lifecycle hooks
    beforeEach(() => {
      client = new BearConsumer(mockProvider.mockService.baseUrl);
    });

    //  Pact annotated code block - Defining the pact, and calling the consumer
    describe("Test Bear species endpoint", () => {
      const expectedResponse = {
        name: "Polar",
        colour: "White",
      };

      // Arrange: declare our expected interactions
      beforeEach(() =>
        mockProvider.addInteraction({
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

      // Act: make the Consumer interact with the mock Provider
      it("Returns a Bear species", () => {
        return client.getSpecies(1).then((resp) => {
          // Assert: check the result is as expected
          expect(resp).toEqual(expectedResponse);
        });
      });
    });
    //  End Pact annotated code block
  }
);
