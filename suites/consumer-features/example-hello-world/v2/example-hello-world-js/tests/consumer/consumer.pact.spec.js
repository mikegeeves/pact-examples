const { Pact } = require("@pact-foundation/pact");
const { BearConsumer } = require("../../src/consumer");
const { BearSpecies } = require("../../src/bear-species");
const { expect } = require("chai");

// Pact annotated code block - Setting up the mock Provider
// Configure our Pact mock Provider
const mockProvider = new Pact({
  consumer: "BearServiceClient",
  provider: "BearService",
  cors: true,
  dir: "./output/pacts",
});
// End Pact annotated code block

describe("Bear API test", () => {
  // Setup Pact lifecycle hooks
  before(() => mockProvider.setup());
  afterEach(() => mockProvider.verify());
  after(() => mockProvider.finalize());

  it("Get Bear species by id", async () => {
    // Pact annotated code block - Defining the pact, and calling the consumer
    // Arrange: declare our expected interactions
    const expectedResponse = {
      name: "Polar",
      colour: "White",
    };

    await mockProvider.addInteraction({
      state: "There are some bears",
      uponReceiving: "A request for the Bear species with id 1",
      willRespondWith: {
        status: 200,
        body: expectedResponse,
      },
      withRequest: {
        method: "GET",
        path: "/species/1",
      },
    });

    // Act: make the Consumer interact with the mock Provider
    const api = new BearConsumer(mockProvider.mockService.baseUrl);
    const bear = await api.getSpecies(1);

    // Assert: check the result is as expected
    expect(bear).to.deep.equal(new BearSpecies("Polar", "White"));
    //  End Pact annotated code block
  });
});
