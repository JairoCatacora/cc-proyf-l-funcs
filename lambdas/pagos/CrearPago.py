import boto3
import json
from datetime import datetime
import urllib3

dynamodb = boto3.resource('dynamodb')
table_payments = dynamodb.Table('pf_pagos')
http = urllib3.PoolManager()

def lambda_handler(event, context):
    try:
        tenant_id = event['body']['tenant_id']
        pago_id = event['body']['pago_id']
        order_id = event['body']['order_id']
        user_id = event['body']['user_id']
        user_info = event['body']['user_info']

        fecha_pago = datetime.utcnow().isoformat()

        url = f"https://3j1d1u98t7.execute-api.us-east-1.amazonaws.com/dev/orden/search?user_id={user_id}&order_id={order_id}"
        response = http.request('GET', url)
        product_data = json.loads(response.data.decode('utf-8'))['body']
        total = Decimal(str(product_data['totoal_price']))

        table_payments.put_item(
            Item={
                'tenant_id': tenant_id,
                'pago_id': payment_id,
                'order_id': order_id,
                'total': total,
                'fecha_pago': fecha_pago,
                'user_info': user_info
            }
        )

        url = f"https://3j1d1u98t7.execute-api.us-east-1.amazonaws.com/dev/orden/update"
        body = json.dumps({
            "tenant_id" : tenant_id,
            "order_id" : order_id,
            "order_status" : 'APPROVED PAYMENT'
        })
        response = http.request('POST', url, body)

        return {
            'statusCode': 201,
            'body': {'message': 'Payment created successfully', 'payment_id': payment_id}
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': {'message': f"Error creating payment: {str(e)}"}
        }
