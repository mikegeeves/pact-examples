FROM debian:no

RUN apt-get update -y && \
    apt-get install -y git g++ python3 build-essential && \
    rm -rf /var/lib/apt/lists/*

RUN ccurl -fsSL https://deb.nodesource.com/setup_current.x | bash - &&\
    apt-get install -y nodejs

# RUN chown -R 501:0 "/.npm"

# COPY ./ /app/
# WORKDIR /app
# RUN make deps
# CMD ["make", "test"]