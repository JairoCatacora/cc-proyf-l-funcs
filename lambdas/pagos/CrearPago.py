import boto3
import json
import datetime
import requests 

def lambda_handler(event, context):
    tenant_id = event['body']['tenant_id']
    pago_id = event['body']['pago_id']
    user_id = event['body']['user_id']
    pago_amount = event['body']['pago_amount']
    user_info = event['body']['user_info']
    productos_id = event['body']['productos_id']

    try:
        response = requests.get(f"https://pfj6am2bx0.execute-api.us-east-1.amazonaws.com/dev/product/search?tenant_id={tenant_id}&product_id={producto_id}")
        response_data = response.json()
        precio_producto = response_data['precio']

        # Validar que el pago_amount coincida con el precio del producto
        if pago_amount != precio_producto:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Pago amount does not match product price'})
            }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': f'Error fetching product data: {str(e)}'})
        }

    # Fecha y hora del pago en UTC
    timestamp = datetime.datetime.utcnow().isoformat()

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('t_pagos')

    table.put_item(
        Item={
            'tenant_id': tenant_id,
            'pago_id': pago_id,
            'user_id': user_id,
            'pago_amount': pago_amount,
            'user_address' : user_address,
            'user_phone' : user_phone,
            'timestamp': timestamp 
        }
    )

    return {
        'statusCode': 201,
        'body': json.dumps({'message': 'Pago created successfully'})
    }
