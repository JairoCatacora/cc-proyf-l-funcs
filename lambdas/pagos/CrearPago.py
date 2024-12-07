import boto3
import json
from boto3.dynamodb.conditions import Key
from datetime import datetime
from decimal import Decimal
import urllib3

dynamodb = boto3.resource('dynamodb')
table_orders = dynamodb.Table('pf_ordenes')
table_payments = dynamodb.Table('pf_pagos')

def validate_token(token):
    url = "https://cdy2ifofu6.execute-api.us-east-1.amazonaws.com/prod/token/validate"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    http = urllib3.PoolManager()
    response = http.request("POST", url, headers=headers)
    
    if response.status == 200:
        return json.loads(response.data.decode('utf-8'))
    else:
        error_msg = json.loads(response.data.decode('utf-8')).get('error', 'Token no válido')
        raise Exception(error_msg)

def search_order(tu_id, order_id):
    if not tu_id or not order_id:
        raise ValueError("tu_id y order_id son requeridos.")
    
    response = table_orders.query(
        IndexName='tu_id-order_id-index',
        KeyConditionExpression=Key('tu_id').eq(tu_id) & Key('order_id').eq(order_id)
    )
    
    if not response.get('Items'):
        raise ValueError("Orden no encontrada.")
    
    return response['Items'][0]

def update_order(tenant_id, order_id, order_status):
    response = table_orders.update_item(
        Key={
            "tenant_id": tenant_id,
            "order_id": order_id
        },
        UpdateExpression="SET order_status = :status",
        ExpressionAttributeValues={
            ":status": order_status
        },
        ReturnValues="UPDATED_NEW"
    )
    return response['Attributes']

def lambda_handler(event, context):
    try:
        token = event.get('headers', {}).get('Authorization', '').split(' ')[1] if 'Authorization' in event.get('headers', {}) else None
        if not token:
            return {
                'statusCode': 400,
                'body': { "message": "Token is required" }
            }
        try:
            validate_token(token)
        except Exception as error:
            return {
                'statusCode': 403,
                'body': { "message": str(error) }
            }

        if isinstance(event['body'], str):
            event['body'] = json.loads(event['body'])

        tenant_id = event['body']['tenant_id']
        pago_id = event['body']['pago_id']
        order_id = event['body']['order_id']
        user_id = event['body']['user_id']
        user_info = event['body']['user_info']

        tu_id = f'{tenant_id}#{user_id}'
        fecha_pago = datetime.utcnow().isoformat()

        try:
            order_data = search_order(tu_id, order_id)
        except ValueError as e:
            return {
                'statusCode': 404,
                'body': {'message': str(e)}
            }

        total = Decimal(str(order_data['total_price']))

        table_payments.put_item(
            Item={
                'tenant_id': tenant_id,
                'pago_id': pago_id, 
                'tu_id': tu_id,
                'order_id': order_id,
                'user_id': user_id,
                'total': total,
                'fecha_pago': fecha_pago,
                'user_info': user_info
            }
        )

        update_order(tenant_id, order_id, 'APPROVED PAYMENT')

        return {
            'statusCode': 201,
            'body': {'message': 'Payment created successfully', 'payment_id': pago_id}
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': {'message': f"Error creating payment: {str(e)}"}
        }
