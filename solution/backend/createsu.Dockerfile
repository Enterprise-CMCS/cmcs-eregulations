FROM public.ecr.aws/lambda/python:3.12

ARG BUILD_ID=env
RUN echo "BUILD_ID is: ${BUILD_ID}"

# Install system dependencies
RUN dnf install -y \
    gcc \
    python3-devel \
    postgresql-devel \
    && dnf clean all

# Copy UV files
COPY ["pyproject.toml", "${LAMBDA_TASK_ROOT}/"]
COPY [".python-version", "${LAMBDA_TASK_ROOT}/"]
COPY ["uv.lock", "${LAMBDA_TASK_ROOT}/"]

# Install and run UV
RUN pip install --no-cache-dir --upgrade pip setuptools uv
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
RUN uv sync --locked --no-install-project

# Copy function code
COPY . ${LAMBDA_TASK_ROOT}/

# Make sure Django can write to tmp
RUN chmod 777 /tmp

# Use the Lambda runtime interface
CMD [ "createsu.handler" ]
