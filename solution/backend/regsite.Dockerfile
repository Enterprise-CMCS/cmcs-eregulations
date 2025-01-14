FROM public.ecr.aws/lambda/python:3.12

# Set Django environment variables
ENV DJANGO_SETTINGS_MODULE=cmcs_regulations.settings.deploy
ENV PYTHONPATH=/var/task
ENV LAMBDA_TASK_ROOT=/var/task
ENV DJANGO_CONFIGURATION=Production
ENV PYTHONUNBUFFERED=1
ENV AWS_LAMBDA_LOG_LEVEL=DEBUG

# Install system dependencies
RUN dnf install -y \
    gcc \
    python3-devel \
    postgresql-devel \
    && dnf clean all

# Copy requirements file
COPY requirements.txt ${LAMBDA_TASK_ROOT}/

# Install Python dependencies
RUN pip install -r ${LAMBDA_TASK_ROOT}/requirements.txt

# Copy function code
COPY . ${LAMBDA_TASK_ROOT}/

# Copy debug handler
COPY debug_handler.py ${LAMBDA_TASK_ROOT}/handler.py

# Make sure Django can write to tmp
RUN chmod 777 /tmp

# Use the Lambda runtime interface
CMD [ "handler.lambda_handler" ]