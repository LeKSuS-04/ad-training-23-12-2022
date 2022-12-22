FROM python:3.10.8-alpine

RUN apk add curl

ADD src /app

WORKDIR /app

CMD ["python", "main.py"]
