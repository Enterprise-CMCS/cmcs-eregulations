FROM public.ecr.aws/lambda/python:3.12

# Copy function code
COPY embedding-generator ${LAMBDA_TASK_ROOT}/app

# Install the required packages
RUN pip install -r app/requirements.txt

CMD [ "app.embedding_generator.handler" ]
