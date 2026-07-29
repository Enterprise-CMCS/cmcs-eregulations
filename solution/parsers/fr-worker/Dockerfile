FROM public.ecr.aws/lambda/python:3.12

RUN pip install --no-cache-dir uv

COPY parsers/fr-worker/pyproject.toml ./pyproject.toml
COPY parsers/fr-worker/uv.lock ./uv.lock
RUN uv export --frozen --no-dev --format requirements-txt --output-file requirements.lock
RUN uv pip install --system -r requirements.lock

COPY parsers/fr-worker/app.py ./app.py

CMD ["app.handler"]
