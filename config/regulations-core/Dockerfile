FROM python:3.8-alpine

COPY [".", "/app/src/"]

WORKDIR /app/src/
RUN apk --update add ca-certificates build-base postgresql-dev \
    && update-ca-certificates \
    && rm -rf /var/cache/apk/*
RUN pip install --no-cache-dir --upgrade pip \
    && pip install psycopg2 \
    && pip install .

ENV PYTHONUNBUFFERED="1"
EXPOSE 8080

CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]
