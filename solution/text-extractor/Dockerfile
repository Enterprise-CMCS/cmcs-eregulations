FROM public.ecr.aws/lambda/python:3.12

ENV HOSTNAME="text-extractor"
ENV EXTERNAL_PORT="6000"
ENV PROXY_PARAMS="--enable-async"
ENV STARTUP_CMD="app.text_extractor.handler"

# Copy function code
# Will be overridden locally
COPY text-extractor ${LAMBDA_TASK_ROOT}/app

# Install binary dependencies
RUN dnf install -y poppler-utils

# Install the required packages
RUN pip install -r app/requirements.txt

# Copy lambda-proxy
COPY lambda-proxy /proxy

# Install packages required by lambda-proxy
RUN pip install -r /proxy/requirements.txt

# Set the custom entrypoint to run lambda-proxy on startup
ENTRYPOINT /proxy/startup.sh
