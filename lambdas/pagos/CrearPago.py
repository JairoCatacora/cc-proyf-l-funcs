import boto3
import json
import datetime
import requests

def lambda_handler(event, context):
    tenant_id = event['body']['tenant_id']
    user_id = event['body']['user_id']
    products = event['body']['products'] 

    try:
        total_amount = 0
        for product in products:
            response = requests.get(f"url/{product['product_id']}")
            product_data = response.json()
            total_amount += product_data['product_price'] * product['quantity']

        user_response = requests.get(f"url/users/{user_id}")
        user_data = user_response.json()

        user_info = {
            "user_address": user_data['user_address'],
            "user_phone": user_data['user_phone']
        }

        dynamodb = boto3.resource('dynamodb')
        payments_table = dynamodb.Table('pf_pagos')

        payment_id = str(uuid.uuid4())
        payment_item = {
            'tenant_id': tenant_id,
            'payment_id': payment_id,
            'user_id': user_id,
            'products': products,
            'total': total_amount,
            'user_info': user_info,
            'timestamp': datetime.datetime.utcnow().isoformat()
        }

        payments_table.put_item(Item=payment_item)

        return {
            'statusCode': 201,
            'body': json.dumps({'message': 'Payment created successfully', 'payment_id': payment_id, 'total': total_amount, 'user_info': user_info})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': f'Error al crear el pago: {str(e)}'})
        }
