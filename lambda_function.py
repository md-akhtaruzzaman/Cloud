import json
import urllib.parse
import requests

def lambda_handler(event, context):
    try:
        # Parse body from POST event
        body = json.loads(event.get('body', '{}'))
        #email = body.get('email')
        question = body.get('question')
        email = event['queryStringParameters'].get('email')

        if not email or not question:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing email or question'})
            }

        # Step 1: GET user info
        user_api = f"https://46styl68r8.execute-api.us-east-1.amazonaws.com/test/user?email={urllib.parse.quote(email)}"
        user_headers = {'User-Agent': 'PostmanRuntime/7.32.3'}
        user_response = requests.get(user_api, headers=user_headers)
        user_response.raise_for_status()
        user_json = user_response.json()

        # Step 2: Extract role
        role = user_json.get('role')
        if not role:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Role not found in user response'})
            }

        # Step 3: Call Lambda endpoint with OPTIONS
        lambda_url = f"https://46styl68r8.execute-api.us-east-1.amazonaws.com/bedrock/bedrock?role={urllib.parse.quote(role)}&question={urllib.parse.quote(question)}"
        lambda_headers = {'User-Agent': 'PostmanRuntime/7.32.3'}
        lambda_response = requests.options(lambda_url, headers=lambda_headers)
        lambda_response.raise_for_status()

        lambda_raw_json = lambda_response.json()

        # Step 4: Parse nested JSON body
        if 'body' not in lambda_raw_json:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Invalid Lambda response (missing body)'})
            }

        inner_body = json.loads(lambda_raw_json['body'])
        answer = inner_body.get('answer')

        if not answer:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Answer not found in Lambda response'})
            }

        return {
            'statusCode': 200,
            'body': json.dumps({'answer': answer})
        }

    except requests.exceptions.RequestException as e:
        return {
            'statusCode': 502,
            'body': json.dumps({'error': f'HTTP error: {str(e)}'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Unhandled error: {str(e)}'})
        }
