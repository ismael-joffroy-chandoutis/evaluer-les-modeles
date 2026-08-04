FROM ubuntu:24.04

RUN apt-get update && apt-get install -y python3 python3-lxml curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY plans.csv /app/plans.csv
