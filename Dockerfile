FROM python:3-alpine

COPY ["requirements.txt", "/app/src/"]
WORKDIR /app/src/

RUN apk --update add ca-certificates build-base postgresql-dev \
    && update-ca-certificates \
    && rm -rf /var/cache/apk/*

RUN pip install --no-cache-dir --upgrade pip setuptools \
    && pip install -r requirements.txt

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]