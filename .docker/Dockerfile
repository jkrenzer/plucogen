FROM python:3.11-alpine as base

# Setup base environment

ARG WORK_DIR="/work"
ARG CACHE_DIR="/usr/local/share/cached"

LABEL maintaner="Jörn Krenzer <container@joern.krenzer.space>"
LABEL org.opencontainers.image.authors="Jörn Krenzer <container@joern.krenzer.space>"
LABEL org.opencontainers.image.licenses="LGPL-3.0-or-later"
LABEL org.opencontainers.image.source="https://gitlab.krenzer.space/software/plucogen/core"
LABEL org.opencontainers.image.url="https://gitlab.krenzer.space/software/plucogen/core"
LABEL org.opencontainers.image.version="0.0.3"

ENV WORK_DIR=${WORK_DIR}
ENV CACHE_DIR=${CACHE_DIR}

SHELL ["/bin/ash", "-c"]
RUN mkdir -p ${WORK_DIR}
WORKDIR ${WORK_DIR}
RUN apk --no-cache add \
    git\
    git-lfs
RUN pip --no-cache-dir install poetry
RUN poetry config virtualenvs.create false

FROM base as installer
COPY ./ ./
RUN apk --no-cache add\
    g++\
    gcc

FROM base as dev
ARG WORK_DIR
ARG CACHE_DIR
ENV WORK_DIR=${WORK_DIR}
ENV CACHE_DIR=${CACHE_DIR}
COPY --from=installer /usr/local /usr/local
COPY ./* ${WORK_DIR}
RUN poetry install --with=dev

FROM dev AS vscode-dev
ARG WORK_DIR
ARG CACHE_DIR
ENV WORK_DIR=${WORK_DIR}
ENV CACHE_DIR=${CACHE_DIR}
ENV EDITOR="code --wait"
RUN git config --global core.editor "${EDITOR}" && \
  git config pull.rebase true

FROM dev as final
