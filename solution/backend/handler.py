# import os
# from django.core.asgi import get_asgi_application
# from mangum import Mangum

# # Make sure your Django settings module is properly set.
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmcs_regulations.settings")

# # Initialize Django ASGI application once, at cold start
# django_asgi_app = get_asgi_application()

# def lambda_handler(event, context):
#     """
#     Lambda entrypoint for Django + ASGI with Mangum.
    
#     This assumes your API Gateway is configured with a stage path 
#     like /eph-1522 or /dev, etc. We want Django's reversed URLs 
#     to include that same path. 
#     """

#     # 1) Check environment variables & API Gateway context
#     stage_env = os.environ.get('STAGE_ENV', '')  # e.g. 'eph-1522', 'dev', 'prod'
#     stage_from_event = event.get('requestContext', {}).get('stage', '')  # e.g. 'eph-1522'
    
#     # Log for debugging in CloudWatch
#     print(f"STAGE_ENV (from Lambda env): {stage_env}")
#     print(f"API Gateway stage (from event): {stage_from_event}")


#     if stage_env:
#         base_path = f"/{stage_env}"
#     elif stage_from_event:
#         base_path = f"/{stage_from_event}"
#     else:
#         base_path = ""

#     # Force Django to build reversed URLs under this base path
#     os.environ["FORCE_SCRIPT_NAME"] = base_path
#     print(f"Setting FORCE_SCRIPT_NAME to: {base_path}")

#     # 3) Construct the Mangum handler.
#     #    - Set api_gateway_base_path to '' so Mangum does NOT strip anything.
#     #    - That way, the incoming path /eph-1522 is left intact for Django.
#     handler = Mangum(
#         django_asgi_app,
#         lifespan="off",
#         api_gateway_base_path=base_path,  # keep the full path
#     )
    
#     # 4) Invoke Mangum
#     try:
#         response = handler(event, context)
#         return response
#     except Exception as e:
#         print(f"Error handling request: {e}")
#         # Re-raise so Lambda logs the error stack trace
#         raise
# import os
# import json
# from django.core.asgi import get_asgi_application
# from mangum import Mangum

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmcs_regulations.settings")

# django_asgi_app = get_asgi_application()

# def lambda_handler(event, context):
#     # For debugging
#     print("=== EVENT ===")
#     print(json.dumps(event))
    
#     stage_env = os.environ.get('STAGE_ENV', '')
#     # Check what's actually in the request context
#     stage_from_event = event.get('requestContext', {}).get('stage', '')
#     print(f"Lambda Env STAGE_ENV: {stage_env}")
#     print(f"API Gateway Stage: {stage_from_event}")

#     if stage_env:
#         base_path = f"/{stage_env}"
#     elif stage_from_event:
#         base_path = f"/{stage_from_event}"
#     else:
#         base_path = ""

#     # Force Django to use that path for reversed URLs
#     os.environ["FORCE_SCRIPT_NAME"] = base_path
#     print(f"Setting FORCE_SCRIPT_NAME to: {base_path}")

#     # By passing api_gateway_base_path=base_path,
#     # Mangum will strip that segment from the incoming path
#     handler = Mangum(
#         django_asgi_app,
#         lifespan="off",
#         api_gateway_base_path=base_path
#     )

#     return handler(event, context)
"""
WSGI config for cmcs_regulations project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see:
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
from mangum import Mangum

# 1) Point to Django settings if not already set
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmcs_regulations.settings")

# 2) Read the stage name from the environment (passed by CDK, etc.)
stage_env = os.environ.get("STAGE_ENV", "")  # e.g. "dev", "eph-1522", "prod"

# 3) If we have a stage, build the path ("/dev", "/eph-1522", etc.)
base_path = f"/{stage_env}" if stage_env else ""

# 4) Tell Django to include the base path in absolute URLs or redirects
os.environ["FORCE_SCRIPT_NAME"] = base_path

# 5) Load the standard Django WSGI application
application = get_wsgi_application()

# 6) Wrap the Django WSGI app with Mangum, stripping the same base path on inbound requests
lambda_handler = Mangum(application, lifespan="off", api_gateway_base_path=base_path)
