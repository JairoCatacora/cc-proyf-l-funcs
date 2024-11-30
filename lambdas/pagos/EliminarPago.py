import boto3
import json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('pf_pagos')

def lambda_handler(event, context):
    try:
        tenant_id = event['body']['tenant_id']
        pago_id = event['body']['pago_id']

        if not tenant_id or not order_id or not pago_id:
            return {
                'statusCode': 400,
                'body': {'message': 'tenant_id, order_id y pago_id son requeridos.'}
            }

        response = table.delete_item(
            Key={
                'tenant_id': tenant_id,
                'pago_id': pago_id
            },
        )

        return {
            'statusCode': 200,
            'body': {'message': 'Orden eliminada exitosamente'}
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': f'Error al eliminar la orden: {str(e)}'})
        }
