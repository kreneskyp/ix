FROM postgres:15.3
LABEL org.opencontainers.image.source https://github.com/kreneskyp/ix

RUN apt update -y &&  \
    apt install -y postgresql-15-pgvector \
