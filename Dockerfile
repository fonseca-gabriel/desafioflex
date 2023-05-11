FROM python:3.9.16-alpine3.17 as builder

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY app.py .
COPY ./requirements.txt .
COPY ./entrypoint.sh .
COPY ./create_test_database.py .

RUN apk update && apk add --no-cache mariadb-dev build-base && \
    apk add --no-cache --virtual .build-deps gcc musl-dev && \
    apk add --no-cache mysql-client && \
#    pip install --upgrade pip && \
#    pip install -r requirements.txt && \
    apk del .build-deps

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

RUN chmod +x  entrypoint.sh

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
