FROM centos:7

# Use the most recent LTS version, CentOS 7 not supported from v18 onwards
RUN curl -sL https://rpm.nodesource.com/setup_14.x | bash -

RUN yum install -y make nodejs gcc-c++

# This is probably a bad idea:
# https://serverfault.com/questions/894625/safely-upgrade-glibc-on-centos-7
# Rust FFI requires GLIBC 2.18, and CentOS 7 is 2.17
RUN \
    yum install -y wget && \
    wget -q http://ftp.gnu.org/gnu/glibc/glibc-2.18.tar.gz && \
    tar zxvf glibc-2.18.tar.gz && \
    cd glibc-2.18 && \
    mkdir build && \
    cd build && \
    ../configure --prefix=/opt/glibc-2.18 && \
    make -j4 && \
    make install

# Required to avoid the following error during an npm install when running examples
# Log files were not written due to an error writing to the directory: /.npm/_logs
RUN mkdir -p /.npm/_logs && chmod a+w /.npm/_logs
RUN mkdir -p /.npm/_cacache && chmod a+w /.npm/_cacache

# Install required npm dependencies
COPY package.json package-lock.json /deps/
WORKDIR /deps
RUN npm install

# Make the Rust FFI use the glibc installed earlier, use patchelf for this
RUN \
    mkdir patchelf && \
    cd patchelf && \
    wget -q https://github.com/NixOS/patchelf/releases/download/0.17.0/patchelf-0.17.0-x86_64.tar.gz && \
    tar -zxf patchelf-0.17.0-x86_64.tar.gz

# This is a bad bad idea generally, and this as-is doesn't actually work - just experimenting here:
RUN /deps/patchelf/bin/patchelf --set-interpreter /opt/glibc-2.18/lib/ld-linux-x86-64.so.2 /deps/node_modules/@pact-foundation/pact-core/build/Release/libpact_ffi.so
RUN /deps/patchelf/bin/patchelf \
    --set-rpath /opt/glibc-2.18/lib:/usr/lib64 /deps/node_modules/@pact-foundation/pact-core/build/Release/libpact_ffi.so
#ENV LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/opt/glibc-2.18/lib"
