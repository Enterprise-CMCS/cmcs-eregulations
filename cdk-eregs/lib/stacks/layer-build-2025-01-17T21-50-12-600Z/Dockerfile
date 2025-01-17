
FROM public.ecr.aws/lambda/python:3.12

WORKDIR /build

# Copy requirements and install dependencies
COPY requirements.txt .
RUN python3 -m pip install --upgrade pip &&     python3 -m pip install -r requirements.txt     -t /asset/python/lib/python3.12/site-packages     --no-cache-dir --no-warn-script-location ||     (echo "Failed to install Python packages" && exit 1)

# Cleanup unnecessary files
RUN find /asset/python -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true &&     find /asset/python -type f -name "*.pyc" -delete &&     find /asset/python -type f -name "*.pyo" -delete &&     find /asset/python -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true &&     find /asset/python -type d -name "*.dist-info" -exec rm -rf {} + 2>/dev/null || true

# Verify package installation
RUN python3 -m pip list &&     echo "Installed packages in /asset/python:" &&     ls -la /asset/python/lib/python3.12/site-packages

CMD [ "bash" ]
      