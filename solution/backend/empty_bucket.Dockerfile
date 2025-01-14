FROM public.ecr.aws/lambda/python:3.12

# Switch to a non-root user (follows least-privilege)
# The AWS Lambda base image defaults to 'sbx_user1051', but you can be explicit:



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




# Make sure Django can write to tmp
RUN chmod 777 /tmp

# Use the Lambda runtime interface
CMD [ "empty_bucket.handler" ]