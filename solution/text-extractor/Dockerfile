FROM public.ecr.aws/lambda/python:3.12

# Copy function code
COPY text-extractor ${LAMBDA_TASK_ROOT}/app

# Copy common code
COPY lambda-common ${LAMBDA_TASK_ROOT}/lambda_common

# Install binary dependencies
# poppler-utils is required for converting PDFs to images for AWS Textract.
RUN dnf install -y poppler-utils

# Install the required packages
RUN pip install -r app/requirements.txt

# Install packages required by lambda-common
RUN pip install -r lambda_common/requirements.txt

CMD [ "app.text_extractor.handler" ]
