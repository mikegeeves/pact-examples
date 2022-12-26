# For creating an image to serve up the contents of pact-examples using Docusaurus.
# Note: this needs to be in the root rather than docusaurus, since we can't ADD ../pact-examples

FROM node:current-alpine
# RUN npx create-docusaurus@latest pact-examples classic
# ADD pact-examples-docusaurus /pact-examples-docusaurus
# WORKDIR pact-examples-docusaurus
# RUN npm install
# RUN npx docusaurus build

EXPOSE 3000
#CMD npx docusaurus start --host 0.0.0.0
CMD cd pact-examples && npx docusaurus start --host 0.0.0.0
