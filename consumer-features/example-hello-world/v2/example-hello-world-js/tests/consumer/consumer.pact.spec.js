const { Pact } = require("@pact-foundation/pact");
const { BearApiClient } = require("../../src/consumer");
const { Bear } = require("../../src/bear");
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

  it("get bear by name", async () => {
    //  Pact annotated code block - Defining the pact, and calling the consumer
    // (4) Arrange
    const expectedResponse = {
      name: "Polar",
      colour: "White",
    };

    await mockProvider.addInteraction({
      state: "Some bears exist",
      uponReceiving: "a request for the Polar bear species",
      willRespondWith: {
        status: 200,
        body: expectedResponse,
      },
      withRequest: {
        method: "GET",
        path: "/species/Polar",
      },
    });

    // (5) Act
    const api = new BearApiClient(mockProvider.mockService.baseUrl);
    const bear = await api.getSpecies("Polar");

    // (6) Assert that we got the expected response
    expect(bear).to.deep.equal(new Bear("Polar", "White"));
    //  End Pact annotated code block
  });
});
