const { PactV3 } = require("@pact-foundation/pact");
const { BearApiClient } = require("../../src/consumer");
const { BearSpecies } = require("../../src/bear-species");
const { expect } = require("chai");

// Pact annotated code block - Setting up the Consumer
// (2) Configure our Pact library
const mockProvider = new PactV3({
  consumer: "BearServiceClient",
  provider: "BearService",
  cors: true,
  dir: "./output/pacts",
});
// End Pact annotated code block

describe("Bear API test", () => {
  it("get bear by name", async () => {
    //  Pact annotated code block - Defining the pact, and calling the consumer
    // (4) Arrange
    const expectedResponse = {
      name: "Polar",
      colour: "White",
    };

    mockProvider
      .given("There are some bears")
      .uponReceiving("A request for the Polar bear species by name")
      .withRequest({
        method: "GET",
        path: "/species",
        query: { name: "Polar" },
      })
      .willRespondWith({
        status: 200,
        body: { ...expectedResponse },
      });

    return await mockProvider.executeTest(async (mockserver) => {
      // (5) Act
      const api = new BearApiClient(mockserver.url);
      const bear = await api.getSpecies("Polar");

      // (6) Assert that we got the expected response
      expect(bear).to.deep.equal(expectedResponse);
    });

    //  End Pact annotated code block
  });
});
