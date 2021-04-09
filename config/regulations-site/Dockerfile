FROM python:3-alpine

COPY ["manage.py", "setup.py", "/app/src/"]
COPY ["regulations", "/app/src/regulations"]
WORKDIR /app/src/

RUN apk --update add ca-certificates \
    && update-ca-certificates \
    && rm -rf /var/cache/apk/*
RUN pip install --no-cache-dir --upgrade pip setuptools \
    && pip install --no-cache-dir -e . \
    && python manage.py migrate

ENV PYTHONUNBUFFERED="1"
EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]