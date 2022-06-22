FROM python:3.9

MAINTAINER Mike Geeves <mike.geeves@bearly-compiling.com>

ENV DEBIAN_FRONTEND noninteractive

ENV PYENV_ROOT="/.pyenv" \
    PATH="/.pyenv/bin:/.pyenv/shims:$PATH" \
    PYENV_GIT_TAG="v2.3.1"

RUN curl -s -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | sh

ENV PYTHON_VERSION="3.9.13"

RUN \
    pyenv install $PYTHON_VERSION && \
    pyenv virtualenv $PYTHON_VERSION examples && \
    pyenv global examples

RUN \
    pip install -q \
      docker pytest pytest-asyncio pact-python

RUN \
   pip install -q pytest-mock

ENV TERM="xterm"
