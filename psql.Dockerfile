FROM postgres:15.3

RUN apt update -y &&  \
    apt install -y postgresql-15-pgvector \
