FROM public.ecr.aws/lambda/python:3.12

RUN pip install --no-cache-dir uv

COPY parsers/ecfr-worker/pyproject.toml ./pyproject.toml
COPY parsers/ecfr-worker/uv.lock ./uv.lock
RUN uv export --frozen --no-dev --format requirements-txt --output-file requirements.lock
RUN uv pip install --system -r requirements.lock

COPY parsers/ecfr-worker ${LAMBDA_TASK_ROOT}/app
COPY parsers/common ./common

CMD ["app.app.handler"]
