// Pact annotated code block - Setting up the Consumer
const { pactWith } = require('jest-pact');
const { BearApiClient } = require('../../src/consumer');

pactWith(
  {
    consumer: 'BearServiceClient',
    provider: 'BearService',
    dir: './output/pacts'
  },
  (provider) => {
    let client;

    beforeEach(() => {
      client = new BearApiClient(provider.mockService.baseUrl);
    });
    // End Pact annotated code block

    //  Pact annotated code block - Defining the pact, and calling the consumer
    describe('test bear endpoint', () => {
      const expectedResponse = {
        name: 'Polar',
        colour: 'White'
      };
      beforeEach(() =>
        provider.addInteraction({
          state: 'Some bears exist',
          uponReceiving: 'a request for the Polar bear species',
          willRespondWith: {
            status: 200,
            body: expectedResponse
          },
          withRequest: {
            method: 'GET',
            path: '/species/Polar'
          }
        })
      );

      it('returns a bear', () => {
        return client.getSpecies('Polar').then((resp) => {
          expect(resp).toEqual(expectedResponse);
        });
      });
    });
    //  End Pact annotated code block
  }
);
