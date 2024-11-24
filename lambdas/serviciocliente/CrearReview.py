import boto3
import json
from datetime import datetime

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('t_reviews')

    tenant_id = event['body']['tenant_id']
    user_id = event['body']['user_id']
    product_id = event['body'].get('product_id')  # Optional for general questions
    order_id = event['body'].get('order_id')      # Optional for order reviews
    question_text = event['body']['question_text']
    review_type = event['body']['review_type']  # e.g., 'product', 'order', 'general'
    timestamp = datetime.utcnow().isoformat()

    if not (tenant_id and user_id and question_text and review_type):
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid request body'})
        }

    table.put_item(
        Item={
            'tenant_id': tenant_id,
            'user_id': user_id,
            'product_id': product_id,
            'order_id': order_id,
            'question_text': question_text,
            'review_type': review_type,
            'timestamp': timestamp,
            'answer': '',
            'answertimestamp': ''
        }
    )

    return {
        'statusCode': 201,
        'body': json.dumps({
            'message': 'Review/Question created successfully',
            'tenant_id': tenant_id,
            'user_id': user_id,
            'review_type': review_type,
            'timestamp': timestamp
        })
    }
