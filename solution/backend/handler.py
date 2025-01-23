import os
from django.core.asgi import get_asgi_application
from mangum import Mangum

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmcs_regulations.settings")

# Initialize Django
django_asgi_app = get_asgi_application()

def lambda_handler(event, context):
    # Debug print the full event
    print("Full event:", event)
    
    stage_env = os.environ.get('STAGE_ENV', '')
    stage = event.get('requestContext', {}).get('stage', '')
    
    print(f"STAGE_ENV: {stage_env}")
    print(f"API Gateway stage: {stage}")

    # Construct base path
    if stage_env.startswith('eph-'):
        base_path = f"/{stage_env}"
    elif stage_env in ['dev', 'val', 'prod']:
        base_path = f"/{stage_env}"
    else:
        base_path = f"/{stage}"

    # Set Django's FORCE_SCRIPT_NAME
    os.environ["FORCE_SCRIPT_NAME"] = base_path
    print(f"Setting FORCE_SCRIPT_NAME to: {base_path}")

    # Initialize Mangum with the correct strip_stage_path setting
    handler = Mangum(
        django_asgi_app, 
        lifespan="off",
        api_gateway_base_path=base_path.lstrip('/'),  # Remove leading slash for Mangum
        strip_stage_path=True  # This ensures the stage path is preserved
    )
    
    # Debug print the processed path
    print("Request path:", event.get('path', ''))
    print("Raw path:", event.get('rawPath', ''))
    
    try:
        response = handler(event, context)
        print("Response:", response)
        return response
    except Exception as e:
        print(f"Error handling request: {e}")
        raise