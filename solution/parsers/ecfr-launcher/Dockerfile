FROM public.ecr.aws/lambda/python:3.12

RUN pip install --no-cache-dir uv

COPY parsers/ecfr-launcher/pyproject.toml ./pyproject.toml
COPY parsers/ecfr-launcher/uv.lock ./uv.lock
RUN uv export --frozen --no-dev --format requirements-txt --output-file requirements.lock
RUN uv pip install --system -r requirements.lock

COPY parsers/ecfr-launcher/app.py ./app.py
COPY parsers/common ./common

CMD ["app.handler"]
