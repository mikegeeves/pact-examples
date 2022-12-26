FROM node:current-alpine
RUN npx create-docusaurus@latest pact-examples classic
WORKDIR pact-examples
#RUN npx docusaurus build

EXPOSE 3000
CMD npx docusaurus start --host 0.0.0.0
