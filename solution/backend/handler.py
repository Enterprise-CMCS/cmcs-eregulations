# import os
# import sys
# import logging
# import traceback
# from cmcs_regulations.wsgi import lambda_handler as wsgi_handler

# # Configure logging
# logging.basicConfig(
#     level=logging.DEBUG,
#     format='%(asctime)s [%(levelname)s] %(message)s',
#     handlers=[logging.StreamHandler(sys.stdout)]
# )
# logger = logging.getLogger()

# def lambda_handler(event, context):
#     try:
#         logger.debug(f"Lambda event: {event}")
#         logger.debug(f"Lambda context: {vars(context)}")
#         logger.debug(f"Environment: {dict(os.environ)}")
        
#         # Call the wsgi handler from cmcs_regulations.wsgi
#         response = wsgi_handler(event, context)
#         logger.debug(f"Lambda response: {response}")
#         return response
#     except Exception as e:
#         logger.error(f"Error processing request: {str(e)}")
#         logger.error(f"Stack trace: {traceback.format_exc()}")
#         return {
#             "statusCode": 500,
#             "body": str(e),
#             "headers": {
#                 "Content-Type": "text/plain",
#             },
#             "isBase64Encoded": False
#         }
# import os
# import sys
# import logging
# import traceback
# import boto3
# from cmcs_regulations.wsgi import lambda_handler as wsgi_handler

# # Configure logging
# logging.basicConfig(
#     level=logging.DEBUG,
#     format='%(asctime)s [%(levelname)s] %(message)s',
#     handlers=[logging.StreamHandler(sys.stdout)]
# )
# logger = logging.getLogger()

# def get_ssm_parameter(param_name):
#     """Fetch parameter from SSM Parameter Store"""
#     try:
#         ssm = boto3.client('ssm')
#         response = ssm.get_parameter(
#             Name=param_name,
#             WithDecryption=True
#         )
#         return response['Parameter']['Value']
#     except Exception as e:
#         logger.error(f"Error fetching SSM parameter {param_name}: {str(e)}")
#         raise

# def setup_environment():
#     """Setup environment variables from SSM parameters"""
#     ssm_params = {
#         'DB_PASSWORD': '/eregulations/db/password',
#         'HTTP_AUTH_USER': '/eregulations/http/user',
#         'HTTP_AUTH_PASSWORD': '/eregulations/http/password',
#         'DJANGO_USERNAME': '/eregulations/http/reader_user',
#         'DJANGO_PASSWORD': '/eregulations/http/reader_password',
#         'DJANGO_ADMIN_USERNAME': '/eregulations/http/user',
#         'DJANGO_ADMIN_PASSWORD': '/eregulations/http/password',
#         'OIDC_RP_CLIENT_ID': '/eregulations/oidc/client_id',
#         'OIDC_RP_CLIENT_SECRET': '/eregulations/oidc/client_secret'
#     }
    
#     for env_var, param_name in ssm_params.items():
#         try:
#             os.environ[env_var] = get_ssm_parameter(param_name)
#         except Exception as e:
#             logger.error(f"Failed to set {env_var}: {str(e)}")
#             raise

# def lambda_handler(event, context):
#     try:
#         logger.debug(f"Lambda event: {event}")
#         logger.debug(f"Lambda context: {vars(context)}")
        
#         # Setup environment variables from SSM
#         setup_environment()
        
#         # Log non-sensitive environment variables
#         safe_env = {k:v for k,v in os.environ.items() 
#                    if not any(secret in k.lower() 
#                             for secret in ['password', 'secret', 'key', 'token'])}
#         logger.debug(f"Safe Environment variables: {safe_env}")
        
#         # Call the wsgi handler from cmcs_regulations.wsgi
#         response = wsgi_handler(event, context)
#         logger.debug(f"Lambda response: {response}")
#         return response
#     except Exception as e:
#         logger.error(f"Error processing request: {str(e)}")
#         logger.error(f"Stack trace: {traceback.format_exc()}")
#         return {
#             "statusCode": 500,
#             "body": str(e),
#             "headers": {
#                 "Content-Type": "text/plain",
#             },
#             "isBase64Encoded": False
#         }
import os
import sys
import logging
import traceback
import boto3
import psycopg2
from cmcs_regulations.wsgi import lambda_handler as wsgi_handler

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger()

def get_ssm_parameter(param_name):
    """Fetch parameter from SSM Parameter Store"""
    try:
        logger.debug(f"Fetching SSM parameter: {param_name}")
        ssm = boto3.client('ssm')
        response = ssm.get_parameter(
            Name=param_name,
            WithDecryption=True
        )
        logger.debug(f"Retrieved SSM parameter: {param_name}")
        return response['Parameter']['Value']
    except Exception as e:
        logger.error(f"Error fetching SSM parameter {param_name}: {str(e)}")
        raise

def setup_environment():
    """Setup environment variables from SSM parameters"""
    ssm_params = {
        'DB_PASSWORD': '/eregulations/db/password',
        'HTTP_AUTH_USER': '/eregulations/http/user',
        'HTTP_AUTH_PASSWORD': '/eregulations/http/password',
        'DJANGO_USERNAME': '/eregulations/http/reader_user',
        'DJANGO_PASSWORD': '/eregulations/http/reader_password',
        'DJANGO_ADMIN_USERNAME': '/eregulations/http/user',
        'DJANGO_ADMIN_PASSWORD': '/eregulations/http/password',
        'OIDC_RP_CLIENT_ID': '/eregulations/oidc/client_id',
        'OIDC_RP_CLIENT_SECRET': '/eregulations/oidc/client_secret'
    }

    logger.debug("Setting up environment variables from SSM parameters")
    for env_var, param_name in ssm_params.items():
        try:
            value = get_ssm_parameter(param_name)
            os.environ[env_var] = value
            if env_var == "DB_PASSWORD":
                logger.debug(f"DB_PASSWORD length: {len(value)}")  # Log only the length
            logger.debug(f"Set environment variable: {env_var}")
        except Exception as e:
            logger.error(f"Failed to set {env_var}: {str(e)}")
            raise

def test_database_connection():
    """Test database connection using environment variables"""
    try:
        db_host = os.environ.get('DB_HOST', 'localhost')
        db_name = os.environ.get('DB_NAME', 'eregulations')
        db_user = os.environ.get('DB_USER', 'eregsuser')
        db_password = os.environ.get('DB_PASSWORD')

        logger.debug(f"Testing database connection to host={db_host}, db={db_name}, user={db_user}")

        conn = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password
        )
        logger.debug("Database connection successful!")
        conn.close()
    except psycopg2.OperationalError as e:
        logger.error(f"Database connection failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error during DB connection: {str(e)}")

def lambda_handler(event, context):
    try:
        logger.debug(f"Lambda event: {event}")
        logger.debug(f"Lambda context: {vars(context)}")

        # Setup environment variables from SSM
        setup_environment()

        # Test database connection
        test_database_connection()

        # Log non-sensitive environment variables
        safe_env = {k: v for k, v in os.environ.items()
                    if not any(secret in k.lower()
                               for secret in ['password', 'secret', 'key', 'token'])}
        logger.debug(f"Safe Environment variables: {safe_env}")

        # Call the wsgi handler from cmcs_regulations.wsgi
        response = wsgi_handler(event, context)
        logger.debug(f"Lambda response: {response}")
        return response
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        logger.error(f"Stack trace: {traceback.format_exc()}")
        return {
            "statusCode": 500,
            "body": str(e),
            "headers": {
                "Content-Type": "text/plain",
            },
            "isBase64Encoded": False
        }