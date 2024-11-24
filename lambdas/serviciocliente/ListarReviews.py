import boto3
import json
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('t_reviews')

    # Extract tenant_id from the request
    tenant_id = event.get('queryStringParameters', {}).get('tenant_id')
    product_id = event.get('queryStringParameters', {}).get('product_id', None)
    user_id = event.get('queryStringParameters', {}).get('user_id', None)

    if not tenant_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'tenant_id is required'})
        }

    # Basic query with tenant_id
    query_params = {
        'KeyConditionExpression': Key('tenant_id').eq(tenant_id)
    }

    # Optionally filter by product_id or user_id
    if product_id:
        query_params['FilterExpression'] = Key('product_id').eq(product_id)
    elif user_id:
        query_params['FilterExpression'] = Key('user_id').eq(user_id)

    try:
        # Query the table using the specified parameters
        response = table.query(**query_params)
        reviews = response.get('Items', [])

        return {
            'statusCode': 200,
            'body': json.dumps(reviews)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Error fetching reviews: {str(e)}'})
        }
