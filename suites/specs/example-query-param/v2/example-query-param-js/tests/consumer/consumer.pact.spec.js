const { Pact } = require("@pact-foundation/pact");
const { BearConsumer } = require("../../src/consumer");
const { BearSpecies } = require("../../src/bear-species");
const { expect } = require("chai");

// Configure our Pact library
const mockProvider = new Pact({
  consumer: "BearServiceClient",
  provider: "BearService",
  cors: true,
  dir: "./output/pacts",
});

describe("Bear API test", () => {
  // Setup Pact lifecycle hooks
  before(() => mockProvider.setup());
  afterEach(() => mockProvider.verify());
  after(() => mockProvider.finalize());

  it("get bear by name", async () => {
    // Arrange
    const expectedResponse = {
      name: "Polar",
      colour: "White",
    };

    // Pact annotated code block - Interaction
    await mockProvider.addInteraction({
      state: "There are some bears",
      uponReceiving: "A request for the Polar bear species by name",
      willRespondWith: {
        status: 200,
        body: expectedResponse,
      },
      withRequest: {
        method: "GET",
        path: "/species",
        // highlight-next-line
        query: { name: "Polar" },
      },
    });
    // End Pact annotated code block

    // Act
    const api = new BearConsumer(mockProvider.mockService.baseUrl);
    const bear = await api.getSpecies("Polar");

    // Assert that we got the expected response
    expect(bear).to.deep.equal(new BearSpecies("Polar", "White"));
  });
});
