###########
# BUILDER #
###########

# pull official base image
FROM python:3.9.16-alpine3.17 as builder

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

COPY app.py .
COPY ./requirements.txt .
COPY ./entrypoint.sh .

RUN apk update && apk add --no-cache mariadb-dev build-base && \
    apk add --no-cache --virtual .build-deps gcc musl-dev && \
    apk add --no-cache mysql-client && \
    pip install -r requirements.txt && \
    apk del .build-deps

# RUN pip install -r requirements.txt
RUN chmod +x  entrypoint.sh

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
