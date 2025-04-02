FROM public.ecr.aws/lambda/python:3.12

# Install system dependencies
RUN dnf install -y \
    gcc \
    python3-devel \
    postgresql-devel \
    && dnf clean all

# Copy requirements file
COPY requirements.txt ${LAMBDA_TASK_ROOT}/requirements.txt

# Install Python dependencies
RUN pip install -r ${LAMBDA_TASK_ROOT}/requirements.txt

# Copy function code
COPY . ${LAMBDA_TASK_ROOT}/

# Make sure Django can write to tmp
RUN chmod 777 /tmp

# Use the Lambda runtime interface
CMD [ "dropdb.handler" ]
