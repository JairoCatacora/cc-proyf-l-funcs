import boto3
import json
from boto3.dynamodb.conditions import Key
from datetime import datetime
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table_orders = dynamodb.Table('pf_ordenes')
table_payments = dynamodb.Table('pf_pagos')

def search_order(user_id, order_id):
    if not user_id or not order_id:
        raise ValueError("user_id y order_id son requeridos.")
    
    response = table_orders.query(
        IndexName='user_id-order_id-index',
        KeyConditionExpression=Key('user_id').eq(user_id) & Key('order_id').eq(order_id)
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
        if isinstance(event['body'], str):
            event['body'] = json.loads(event['body'])

        tenant_id = event['body']['tenant_id']
        pago_id = event['body']['pago_id']
        order_id = event['body']['order_id']
        user_id = event['body']['user_id']
        user_info = event['body']['user_info']

        fecha_pago = datetime.utcnow().isoformat()

        try:
            order_data = search_order(user_id, order_id)
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
                'order_id': order_id,
                'user_id' : user_id,
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
