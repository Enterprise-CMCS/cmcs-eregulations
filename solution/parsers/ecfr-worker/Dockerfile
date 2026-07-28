FROM public.ecr.aws/lambda/python:3.12

COPY parsers/ecfr-worker/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY parsers/ecfr-worker/app.py ./app.py

CMD ["app.handler"]
