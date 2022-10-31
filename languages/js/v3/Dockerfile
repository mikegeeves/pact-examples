FROM node:16

RUN apt-get update -y && \
    apt-get install -y git g++ python3 build-essential && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /.npm/_logs && chmod a+w /.npm/_logs
# COPY ./ /app/
# WORKDIR /app
# RUN npm install
# CMD ["npm", "t"]