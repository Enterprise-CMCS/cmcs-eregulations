# #!/usr/bin/env python3
# import boto3
# import json
# import os
# import requests
# from urllib.parse import urljoin

# def get_api_gateway_endpoint():
#     """
#     Retrieve the API Gateway endpoint from CloudFormation outputs
#     """
#     # Initialize AWS clients
#     cloudformation_client = boto3.client('cloudformation')
    
#     # Stack name format from your CDK stack
#     stack_name = 'cms-eregs-eph-1522-api'  # Adjust this to match your actual stack name
    
#     try:
#         # Describe stack outputs
#         response = cloudformation_client.describe_stacks(StackName=stack_name)
        
#         # Find the API endpoint in the outputs
#         outputs = response['Stacks'][0]['Outputs']
#         api_endpoint = next(
#             (output['OutputValue'] for output in outputs 
#              if output.get('OutputKey') == 'ApiEndpoint'),
#             None
#         )
        
#         return api_endpoint
#     except Exception as e:
#         print(f"Error retrieving API Gateway endpoint: {e}")
#         return None

# def test_api_gateway_endpoint(endpoint, method='GET', payload=None):
#     """
#     Test API Gateway endpoint
#     """
#     if not endpoint:
#         print("No endpoint provided!")
#         return None
    
#     print(f"\n--- API Gateway Endpoint Test ---")
#     print(f"Endpoint: {endpoint}")
    
#     try:
#         # Prepare headers
#         headers = {
#             'Content-Type': 'application/json',
#             # Add any additional headers like authorization if needed
#             # 'Authorization': 'Bearer YOUR_TOKEN'
#         }
        
#         # Determine request method
#         if method.upper() == 'GET':
#             response = requests.get(endpoint, headers=headers)
#         elif method.upper() == 'POST':
#             response = requests.post(
#                 endpoint, 
#                 headers=headers, 
#                 data=json.dumps(payload) if payload else None
#             )
#         else:
#             print(f"Unsupported HTTP method: {method}")
#             return None
        
#         # Print response details
#         print(f"Status Code: {response.status_code}")
#         print("Response Headers:")
#         for header, value in response.headers.items():
#             print(f"{header}: {value}")
        
#         print("\nResponse Body:")
#         try:
#             # Try to parse and pretty print JSON
#             response_json = response.json()
#             print(json.dumps(response_json, indent=2))
#         except ValueError:
#             # If not JSON, print raw text
#             print(response.text)
        
#         return response
    
#     except requests.RequestException as e:
#         print(f"Request error: {e}")
#         return None

# def main():
#     # Get the API Gateway endpoint
#     api_endpoint = get_api_gateway_endpoint()
    
#     if not api_endpoint:
#         print("Could not retrieve API Gateway endpoint!")
#         return
    
#     # Test with different methods and payloads
#     methods_to_test = [
#         {'method': 'GET', 'payload': None},
#         {'method': 'POST', 'payload': {"test": "payload", "timestamp": str(datetime.now())}}
#     ]
    
#     for test_config in methods_to_test:
#         test_api_gateway_endpoint(
#             api_endpoint, 
#             method=test_config['method'], 
#             payload=test_config['payload']
#         )

# if __name__ == '__main__':
#     from datetime import datetime
#     main()
# import requests
# import json

# def test_endpoints():
#     # API Gateway endpoint
#     api_gateway_url = "https://q3vrgyqps4.execute-api.us-east-1.amazonaws.com/prod/"
    
#     # CloudFront endpoint
#     cloudfront_url = "https://d2vawmaot9l5cn.cloudfront.net/"

#     # Common headers
#     headers = {
#         'User-Agent': 'Python Test Client',
#         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
#         'Accept-Language': 'en-US,en;q=0.5',
#         'Accept-Encoding': 'gzip, deflate, br',
#         'Origin': 'https://d2vawmaot9l5cn.cloudfront.net',
#         'Referer': 'https://d2vawmaot9l5cn.cloudfront.net/'
#     }

#     # Test API Gateway
#     print("\n=== Testing API Gateway ===")
#     try:
#         response = requests.get(api_gateway_url, headers=headers)
#         print(f"Status Code: {response.status_code}")
#         print("Response Headers:")
#         for key, value in response.headers.items():
#             print(f"{key}: {value}")
#         print("\nResponse Body:")
#         print(response.text)
#     except Exception as e:
#         print(f"Error with API Gateway: {str(e)}")

#     # Test CloudFront
#     print("\n=== Testing CloudFront ===")
#     try:
#         response = requests.get(cloudfront_url, headers=headers)
#         print(f"Status Code: {response.status_code}")
#         print("Response Headers:")
#         for key, value in response.headers.items():
#             print(f"{key}: {value}")
#         print("\nResponse Body:")
#         print(response.text)
#     except Exception as e:
#         print(f"Error with CloudFront: {str(e)}")

# def test_api_with_data():
#     api_url = "https://q3vrgyqps4.execute-api.us-east-1.amazonaws.com/prod"
    
#     # Data to send
#     data = {
#         "key1": "value1",
#         "key2": "value2"
#     }
    
#     headers = {
#         'Content-Type': 'application/json',
#         'Origin': 'https://d2vawmaot9l5cn.cloudfront.net',
#         'Referer': 'https://d2vawmaot9l5cn.cloudfront.net/'
#     }

#     print("\n=== Testing API with Data ===")
#     try:
#         response = requests.post(api_url, json=data, headers=headers)
#         print(f"Status Code: {response.status_code}")
#         print("Response Headers:")
#         for key, value in response.headers.items():
#             print(f"{key}: {value}")
#         print("\nResponse Body:")
#         print(response.text)
#     except Exception as e:
#         print(f"Error with API request: {str(e)}")

# def test_with_session():
#     session = requests.Session()
#     base_url = "https://q3vrgyqps4.execute-api.us-east-1.amazonaws.com/prod/"
    
#     # Set common headers for session
#     session.headers.update({
#         'User-Agent': 'Python Test Client',
#         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
#         'Origin': 'https://d2vawmaot9l5cn.cloudfront.net',
#         'Referer': 'https://d2vawmaot9l5cn.cloudfront.net/'
#     })

#     print("\n=== Testing with Session ===")
#     try:
#         # First request - might get CSRF token
#         response = session.get(base_url)
#         print(f"Initial Status Code: {response.status_code}")
        
#         # Get CSRF token if available
#         csrf_token = response.cookies.get('csrftoken')
#         if csrf_token:
#             session.headers.update({'X-CSRFToken': csrf_token})
        
#         # Make authenticated request
#         response = session.get(f"{base_url}api/protected-endpoint")
#         print(f"Protected Endpoint Status Code: {response.status_code}")
#         print("Response Headers:")
#         for key, value in response.headers.items():
#             print(f"{key}: {value}")
#         print("\nResponse Body:")
#         print(response.text)
#     except Exception as e:
#         print(f"Error with session request: {str(e)}")
#     finally:
#         session.close()

# if __name__ == "__main__":
#     test_endpoints()
#     test_api_with_data()
#     test_with_session()

# import requests
# import json
# from urllib.parse import urljoin

# def test_static_assets():
#     # CloudFront URL for static assets
#     cloudfront_url = "https://d2vawmaot9l5cn.cloudfront.net/"
    
#     # List of critical static assets to test
#     static_paths = [
#         'static/css/main.css',
#         'static/js/main.js',
#         'static/images/logo.png',
#     ]
    
#     print("\n=== Testing Static Assets via CloudFront ===")
#     for path in static_paths:
#         full_url = urljoin(cloudfront_url, path)
#         try:
#             response = requests.get(full_url)
#             print(f"\nTesting {path}:")
#             print(f"Status Code: {response.status_code}")
#             print(f"Content-Type: {response.headers.get('Content-Type')}")
#             print(f"Content-Length: {response.headers.get('Content-Length')}")
#         except Exception as e:
#             print(f"Error testing {path}: {str(e)}")
import boto3
import requests
import json
import time
from datetime import datetime, timedelta

def test_api_and_logs(stack_name='cms-eregs-eph-1522-api'):
    # Initialize AWS clients
    cloudformation = boto3.client('cloudformation')
    logs_client = boto3.client('logs')

    try:
        # Get stack outputs
        print(f"Getting stack outputs for {stack_name}...")
        stack_response = cloudformation.describe_stacks(StackName=stack_name)
        stack_outputs = {
            output['OutputKey']: output['OutputValue'] 
            for output in stack_response['Stacks'][0]['Outputs']
        }

        api_endpoint = stack_outputs.get('ApiEndpoint')
        api_handler_name = stack_outputs.get('ApiHandlerName')

        print(f"\nAPI Handler Lambda: {api_handler_name}")
        print(f"API Endpoint: {api_endpoint}")

        # Make API request and get initial timestamp
        start_time = int(datetime.now().timestamp() * 1000)
        
        print("\nMaking API request...")
        response = requests.get(api_endpoint)
        print(f"Status code: {response.status_code}")

        # Wait a bit for logs to appear
        print("\nWaiting for logs to propagate...")
        time.sleep(5)

        # Get Lambda logs
        print("\n=== Checking Lambda Logs ===")
        log_group_name = f"/aws/lambda/{api_handler_name}"
        
        try:
            log_streams = logs_client.describe_log_streams(
                logGroupName=log_group_name,
                orderBy='LastEventTime',
                descending=True,
                limit=1
            )
            
            if log_streams['logStreams']:
                stream_name = log_streams['logStreams'][0]['logStreamName']
                print(f"Found log stream: {stream_name}")
                
                logs = logs_client.get_log_events(
                    logGroupName=log_group_name,
                    logStreamName=stream_name,
                    startTime=start_time,
                    limit=100
                )
                
                print("\nRecent logs:")
                for event in logs['events']:
                    timestamp = datetime.fromtimestamp(event['timestamp']/1000).strftime('%Y-%m-%d %H:%M:%S')
                    print(f"{timestamp} - {event['message']}")
            else:
                print("No log streams found")
                
        except Exception as e:
            print(f"Error fetching logs: {e}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api_and_logs()