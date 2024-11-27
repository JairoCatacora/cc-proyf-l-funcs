import boto3
import json
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table_payments = dynamodb.Table('t_payments')

def lambda_handler(event, context):
    try:
        order_id = event['body']['order_id']
        tenant_id = event['body']['tenant_id']
        payment_id = event['body']['payment_id']

        timestamp = datetime.utcnow().isoformat()

        table_payments.put_item(
            Item={
                'order_id': order_id,
                'payment_id': payment_id,
                'tenant_id': tenant_id,
                'total': payment_data['total'],
                'timestamp': timestamp
            }
        )

        return {
            'statusCode': 201,
            'body': json.dumps({'message': 'Payment created successfully', 'payment_id': payment_id})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': f"Error creating payment: {str(e)}"})
        }
