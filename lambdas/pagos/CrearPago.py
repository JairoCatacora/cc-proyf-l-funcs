import boto3
import json
from datetime import datetime
import urllib3
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table_payments = dynamodb.Table('pf_pagos')
http = urllib3.PoolManager()

def lambda_handler(event, context):
    try:
        if isinstance(event['body'], str):
            event['body'] = json.loads(event['body'])

        tenant_id = event['body']['tenant_id']
        pago_id = event['body']['pago_id']
        order_id = event['body']['order_id']
        user_id = event['body']['user_id']
        user_info = event['body']['user_info']

        fecha_pago = datetime.utcnow().isoformat()

        url = f"https://4lnj7a6xu8.execute-api.us-east-1.amazonaws.com/dev/orden/search?user_id={user_id}&order_id={order_id}"
        response = http.request('GET', url)
        search_response = json.loads(response.data.decode('utf-8'))

        if search_response.get('statusCode') != 200 or not search_response['body'].get('orders'):
            return {
                'statusCode': 404,
                'body': {'message': 'Orden no encontrada o error en el servicio de búsqueda.'}
            }

        order_data = search_response['body']['orders'][0]
        total = Decimal(str(order_data['total_price']))


        table_payments.put_item(
            Item={
                'tenant_id': tenant_id,
                'pago_id': pago_id, 
                'order_id': order_id,
                'total': total,
                'fecha_pago': fecha_pago,
                'user_info': user_info
            }
        )

        url = f"https://4lnj7a6xu8.execute-api.us-east-1.amazonaws.com/dev/orden/update"
        update = {
            "tenant_id": tenant_id,
            "order_id": order_id,
            "order_status": 'APPROVED PAYMENT'
        }
        encoded_body = json.dumps(update)

        response = http.request(
            "PATCH",
            url,
            body=encoded_body,
            headers={'Content-Type': 'application/json'}
        )

        return {
            'statusCode': 201,
            'body': {'message': 'Payment created successfully', 'payment_id': pago_id}
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': {'message': f"Error creating payment: {str(e)}"}
        }
