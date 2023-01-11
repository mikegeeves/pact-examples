const { PactV3 } = require("@pact-foundation/pact");
const { BearApiClient } = require("../../src/consumer");
const { BearSpecies } = require("../../src/bear-species");
const { expect } = require("chai");

// Pact annotated code block - Setting up the mock Provider
// Configure our Pact mock Provider
const mockProvider = new PactV3({
  consumer: "BearServiceClient",
  provider: "BearService",
  cors: true,
  dir: "./output/pacts",
});
// End Pact annotated code block

describe("Bear API test", () => {
  it("Get Bear species by id", async () => {
    // Pact annotated code block - Defining the pact, and calling the consumer
    // Arrange: declare our expected interactions
    const expectedResponse = {
      name: "Polar",
      colour: "White",
    };

    mockProvider
      .given("There are some bears")
      .uponReceiving("A request for the Bear species with id 1")
      .withRequest({
        method: "GET",
        path: "/species/1",
      })
      .willRespondWith({
        status: 200,
        body: { ...expectedResponse },
      });

    return await mockProvider.executeTest(async (mockserver) => {
      // Act: make the Consumer interact with the mock Provider
      const api = new BearApiClient(mockserver.url);
      const bear = await api.getSpecies(1);

      // Assert: check the result is as expected
      expect(bear).to.deep.equal(expectedResponse);
    });
    //  End Pact annotated code block
  });
});
