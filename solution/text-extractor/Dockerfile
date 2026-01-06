FROM public.ecr.aws/lambda/python:3.12

# Copy function code
COPY text-extractor ${LAMBDA_TASK_ROOT}/app

# Install binary dependencies
# poppler-utils is required for converting PDFs to images for AWS Textract.
# liberation-fonts is required because the default installed fonts are not sufficient for some PDFs and introduce rendering issues.
RUN dnf install -y poppler-utils liberation-fonts

# Install the required packages
RUN pip install --no-cache-dir --upgrade pip setuptools uv

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_PROJECT_ENVIRONMENT=${LAMBDA_TASK_ROOT}/venv
ENV UV_PROJECT=${LAMBDA_TASK_ROOT}/app/text-extractor

RUN uv sync --locked --no-install-project

CMD [ "app.text-extractor.handler" ]
