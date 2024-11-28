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
        # Verifica si 'body' está presente y es una cadena que necesita ser convertida a un diccionario
        if isinstance(event['body'], str):
            event['body'] = json.loads(event['body'])

        tenant_id = event['body']['tenant_id']
        pago_id = event['body']['pago_id']
        order_id = event['body']['order_id']
        user_id = event['body']['user_id']
        user_info = event['body']['user_info']

        fecha_pago = datetime.utcnow().isoformat()

        # Realiza la llamada GET al endpoint de la orden
        url = f"https://3j1d1u98t7.execute-api.us-east-1.amazonaws.com/dev/orden/search?user_id={user_id}&order_id={order_id}"
        response = http.request('GET', url)
        product_data = json.loads(response.data.decode('utf-8'))['body']
        total = Decimal(str(product_data['total_price']))  # Corregido el nombre del campo

        # Inserta el pago en DynamoDB
        table_payments.put_item(
            Item={
                'tenant_id': tenant_id,
                'pago_id': pago_id,  # Corrección aquí: cambia 'payment_id' a 'pago_id'
                'order_id': order_id,
                'total': total,
                'fecha_pago': fecha_pago,
                'user_info': user_info
            }
        )

        # Llamada POST para actualizar el estado de la orden
        url = f"https://3j1d1u98t7.execute-api.us-east-1.amazonaws.com/dev/orden/update"
        body = {
            "tenant_id": tenant_id,
            "order_id": order_id,
            "order_status": 'APPROVED PAYMENT'
        }
        encoded_body = json.dumps(body)

        response = http.request(
            "POST",
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
