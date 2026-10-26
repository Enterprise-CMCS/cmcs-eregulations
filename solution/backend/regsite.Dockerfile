# Dockerfile adapted for use on Lambda from Astral UV examples:
# https://docs.astral.sh/uv/guides/integration/aws-lambda/#using-uv-with-aws-lambda

FROM ghcr.io/astral-sh/uv:0.9.22 AS uv

# First, bundle the dependencies into the task root.
FROM public.ecr.aws/lambda/python:3.12 AS builder

# Enable bytecode compilation, to improve cold-start performance.
ENV UV_COMPILE_BYTECODE=1

# Disable installer metadata, to create a deterministic layer.
ENV UV_NO_INSTALLER_METADATA=1

# Enable copy mode to support bind mount caching.
ENV UV_LINK_MODE=copy

# Bundle the dependencies into the Lambda task root via `uv pip install --target`.
#
# Omit any local packages (`--no-emit-workspace`) and development dependencies (`--no-dev`).
# This ensures that the Docker layer cache is only invalidated when the `pyproject.toml` or `uv.lock`
# files change, but remains robust to changes in the application code.
RUN --mount=from=uv,source=/uv,target=/bin/uv \
    --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv export --frozen --no-emit-workspace --no-dev --no-editable -o requirements.txt && \
    uv pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

FROM public.ecr.aws/lambda/python:3.12

# Copy the runtime dependencies from the builder stage.
COPY --from=builder ${LAMBDA_TASK_ROOT} ${LAMBDA_TASK_ROOT}

# Set Django environment variables
ENV DJANGO_SETTINGS_MODULE=cmcs_regulations.settings.deploy
ENV PYTHONPATH=/var/task
ENV LAMBDA_TASK_ROOT=/var/task
ENV DJANGO_CONFIGURATION=Production
ENV PYTHONUNBUFFERED=1
ARG BUILD_ID=env
ARG AL2023_RELEASE=2023.12.20261026
RUN dnf clean all && \
    dnf --releasever="${AL2023_RELEASE}" update -y pcre2 && \
    dnf clean all && \
    PCRE2_RELEASE="$(rpm -q --qf '%{RELEASE}' pcre2)" && \
    echo "PCRE2 release: ${PCRE2_RELEASE}" && \
    case "${PCRE2_RELEASE}" in \
        1.amzn2023.0.[5-9]|1.amzn2023.0.[1-9][0-9]*) ;; \
        *) echo "PCRE2 release ${PCRE2_RELEASE} is older than fixed 1.amzn2023.0.5" >&2; exit 1 ;; \
    esac && \
    echo "BUILD_ID is: ${BUILD_ID}"

# Copy function code
COPY . ${LAMBDA_TASK_ROOT}/

# Use the Lambda runtime interface
CMD [ "handler.lambda_handler" ]
