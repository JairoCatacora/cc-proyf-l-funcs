import boto3
import json
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table_orders = dynamodb.Table('pf_ordenes')
table_payments = dynamodb.Table('pf_pagos')

def search_payment(order_id, pago_id):
    response = table_payments.query(
        IndexName='order_id-pago_id-index',
        KeyConditionExpression=Key('order_id').eq(order_id) & Key('pago_id').eq(pago_id)
    )
    return response.get('Items', [])

def delete_payment(tenant_id, pago_id):
    table_payments.delete_item(
        Key={
            'tenant_id': tenant_id,
            'pago_id': pago_id
        }
    )

def delete_order(tenant_id, order_id):
    table_orders.delete_item(
        Key={
            'tenant_id': tenant_id,
            'order_id': order_id
        }
    )

def lambda_handler(event, context):
    try:
        if isinstance(event['body'], str):
            event['body'] = json.loads(event['body'])

        tenant_id = event['body']['tenant_id']
        order_id = event['body']['order_id']
        pago_id = event['body'].get('pago_id')

        if not tenant_id or not order_id:
            return {
                'statusCode': 400,
                'body': {'message': 'tenant_id y order_id son requeridos.'}
            }

        if pago_id:
            pagos = search_payment(order_id, pago_id)
            if pagos:
                delete_payment(tenant_id, pago_id)
                message = "Pago y orden eliminados exitosamente."
            else:
                message = "No se encontró el pago asociado. Solo se eliminará la orden."
        else:
            message = "Pago no proporcionado. Solo se eliminará la orden."

        delete_order(tenant_id, order_id)

        return {
            'statusCode': 200,
            'body': {'message': message}
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': {'message': f'Error al procesar la solicitud: {str(e)}'}
        }