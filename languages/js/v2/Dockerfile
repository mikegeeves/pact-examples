FROM node:18

RUN apt-get update -y && \
    apt-get install -y git g++ python3 build-essential && \
    rm -rf /var/lib/apt/lists/*

# Required to avoid the following error during an npm install when running examples
# Log files were not written due to an error writing to the directory: /.npm/_logs
RUN mkdir -p /.npm/_logs && chmod a+w /.npm/_logs
RUN mkdir -p /.npm/_cacache && chmod a+w /.npm/_cacache

# Install required npm dependencies
COPY package.json package-lock.json /npm/
WORKDIR /npm
RUN npm install
