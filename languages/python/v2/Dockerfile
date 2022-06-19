FROM python:3.9

MAINTAINER Mike Geeves <mike.geeves@bearly-compiling.com>

ENV DEBIAN_FRONTEND noninteractive

ENV PYENV_ROOT="/.pyenv" \
    PATH="/.pyenv/bin:/.pyenv/shims:$PATH" \
    PYENV_GIT_TAG="v2.3.1"

RUN curl -s -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | sh
