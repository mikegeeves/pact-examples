const { Pact } = require("@pact-foundation/pact");
const { BearApiClient } = require("../../src/consumer");
const { BearSpecies } = require("../../src/bear-species");
const { expect } = require("chai");

// Pact annotated code block - Setting up the Consumer
// (2) Configure our Pact library
const mockProvider = new Pact({
  consumer: "BearServiceClient",
  provider: "BearService",
  cors: true,
  dir: "./output/pacts",
});

describe("Bear API test", () => {
  // (3) Setup Pact lifecycle hooks
  before(() => mockProvider.setup());
  afterEach(() => mockProvider.verify());
  after(() => mockProvider.finalize());
  // End Pact annotated code block

  it("Get Bear species by id", async () => {
    //  Pact annotated code block - Defining the pact, and calling the consumer
    // (4) Arrange
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

    // (5) Act
    const api = new BearApiClient(mockProvider.mockService.baseUrl);
    const bear = await api.getSpecies(1);

    // (6) Assert that we got the expected response
    expect(bear).to.deep.equal(new BearSpecies("Polar", "White"));
    //  End Pact annotated code block
  });
});
