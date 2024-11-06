import boto3
import json

def lambda_handler(event, context):
    body = json.loads(event['body'])
    tenant_id = body['tenant_id']
    pago_id = body['pago_id']
    user_id = body['user_id']
    pago_info = body['pago_info']

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('t_pagos')

    table.put_item(
        Item={
            'tenant_id': tenant_id,
            'pago_id': pago_id,
            'user_id': user_id,
            'pago_info': pago_info
        }
    )

    return {
        'statusCode': 201,
        'body': json.dumps({'message': 'Pago created successfully'})
    }
