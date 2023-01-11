const { PactV3 } = require("@pact-foundation/pact");
const { BearConsumer } = require("../../src/consumer");
const { BearSpecies } = require("../../src/bear-species");
const { expect } = require("chai");

// Configure our Pact library
const mockProvider = new PactV3({
  consumer: "BearServiceClient",
  provider: "BearService",
  cors: true,
  dir: "./output/pacts",
});

describe("Bear API test", () => {
  it("get bear by name", async () => {
    // Arrange
    const expectedResponse = {
      name: "Polar",
      colour: "White",
    };

    // Pact annotated code block - Interaction
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
    // End Pact annotated code block

    return await mockProvider.executeTest(async (mockserver) => {
      // Act
      const api = new BearConsumer(mockserver.url);
      const bear = await api.getSpecies("Polar");

      // Assert that we got the expected response
      expect(bear).to.deep.equal(expectedResponse);
    });

    //  End Pact annotated code block
  });
});
