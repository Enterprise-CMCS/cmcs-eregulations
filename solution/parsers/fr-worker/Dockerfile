FROM public.ecr.aws/lambda/python:3.12

COPY parsers/fr-worker/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY parsers/fr-worker/app.py ./app.py

CMD ["app.handler"]
