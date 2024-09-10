FROM postgres:latest

ENV POSTGRES_USER=aiconsole
ENV POSTGRES_PASSWORD=aiconsole
ENV POSTGRES_DB=materials

COPY ./init.sql /docker-entrypoint-initdb.d/

EXPOSE 5432
