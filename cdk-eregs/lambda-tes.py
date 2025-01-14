#!/usr/bin/env python3
import boto3
import json
import os
import requests
from urllib.parse import urljoin

def get_api_gateway_endpoint():
    """
    Retrieve the API Gateway endpoint from CloudFormation outputs
    """
    # Initialize AWS clients
    cloudformation_client = boto3.client('cloudformation')
    
    # Stack name format from your CDK stack
    stack_name = 'cms-eregs-eph-1516-api'  # Adjust this to match your actual stack name
    
    try:
        # Describe stack outputs
        response = cloudformation_client.describe_stacks(StackName=stack_name)
        
        # Find the API endpoint in the outputs
        outputs = response['Stacks'][0]['Outputs']
        api_endpoint = next(
            (output['OutputValue'] for output in outputs 
             if output.get('OutputKey') == 'ApiEndpoint'),
            None
        )
        
        return api_endpoint
    except Exception as e:
        print(f"Error retrieving API Gateway endpoint: {e}")
        return None

def test_api_gateway_endpoint(endpoint, method='GET', payload=None):
    """
    Test API Gateway endpoint
    """
    if not endpoint:
        print("No endpoint provided!")
        return None
    
    print(f"\n--- API Gateway Endpoint Test ---")
    print(f"Endpoint: {endpoint}")
    
    try:
        # Prepare headers
        headers = {
            'Content-Type': 'application/json',
            # Add any additional headers like authorization if needed
            # 'Authorization': 'Bearer YOUR_TOKEN'
        }
        
        # Determine request method
        if method.upper() == 'GET':
            response = requests.get(endpoint, headers=headers)
        elif method.upper() == 'POST':
            response = requests.post(
                endpoint, 
                headers=headers, 
                data=json.dumps(payload) if payload else None
            )
        else:
            print(f"Unsupported HTTP method: {method}")
            return None
        
        # Print response details
        print(f"Status Code: {response.status_code}")
        print("Response Headers:")
        for header, value in response.headers.items():
            print(f"{header}: {value}")
        
        print("\nResponse Body:")
        try:
            # Try to parse and pretty print JSON
            response_json = response.json()
            print(json.dumps(response_json, indent=2))
        except ValueError:
            # If not JSON, print raw text
            print(response.text)
        
        return response
    
    except requests.RequestException as e:
        print(f"Request error: {e}")
        return None

def main():
    # Get the API Gateway endpoint
    api_endpoint = get_api_gateway_endpoint()
    
    if not api_endpoint:
        print("Could not retrieve API Gateway endpoint!")
        return
    
    # Test with different methods and payloads
    methods_to_test = [
        {'method': 'GET', 'payload': None},
        {'method': 'POST', 'payload': {"test": "payload", "timestamp": str(datetime.now())}}
    ]
    
    for test_config in methods_to_test:
        test_api_gateway_endpoint(
            api_endpoint, 
            method=test_config['method'], 
            payload=test_config['payload']
        )

if __name__ == '__main__':
    from datetime import datetime
    main()