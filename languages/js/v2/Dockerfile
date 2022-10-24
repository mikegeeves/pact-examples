FROM debian:stretch

RUN apt-get update -y && \
    apt-get install -y git g++ python3 build-essential curl && \
    rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://deb.nodesource.com/setup_current.x | bash - && \
    apt-get install -y nodejs \
    build-essential && \
    node --version && \ 
    npm --version

# COPY ./ /app/
# WORKDIR /app
# RUN make deps
# CMD ["npm", "t"]