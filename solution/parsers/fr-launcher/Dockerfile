FROM public.ecr.aws/lambda/python:3.12

COPY parsers/fr-launcher/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY parsers/fr-launcher/app.py ./app.py

CMD ["app.handler"]
