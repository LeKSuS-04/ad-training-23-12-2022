FROM ubuntu:22.04
RUN apt-get update && apt-get install libpq-dev socat sudo postgresql-client -yqq \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY ./src/* ./

CMD ["/app/server.sh"]
