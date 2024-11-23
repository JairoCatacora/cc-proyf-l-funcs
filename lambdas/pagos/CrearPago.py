import boto3
import json
import datetime
import requests  # Asegúrate de incluir esta librería en el entorno de Lambda si es necesaria

def lambda_handler(event, context):
    body = json.loads(event['body'])
    tenant_id = body['tenant_id']
    pago_id = body['pago_id']
    user_id = body['user_id']
    pago_amount = body['pago_amount']
    user_address = body['user_address']
    user_phone = body['user_phone']
    producto_id = body['producto_id']  # Asegúrate de tener el ID del producto

    # Llamada al microservicio de productos para obtener el precio
    try:
        response = requests.get(f"https://tu-microservicio-productos.com/productos/{producto_id}")
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
            'timestamp': timestamp  # Agregando la fecha y hora del pago
        }
    )

    return {
        'statusCode': 201,
        'body': json.dumps({'message': 'Pago created successfully'})
    }
