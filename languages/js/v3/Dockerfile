FROM node:18

RUN apt-get update -y && \
    apt-get install -y git g++ python3 build-essential && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /.npm/_logs && chmod a+w /.npm/_logs
RUN mkdir -p /.npm/_cacache && chmod a+w /.npm/_cacache