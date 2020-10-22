FROM python:3-alpine

COPY [".", "/app/src/"]

WORKDIR /app/src

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "app.py"]
