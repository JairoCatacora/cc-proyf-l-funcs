import boto3
import json

def lambda_handler(event, context):
    body = json.loads(event['body'])
    tenant_id = body['tenant_id']
    pago_id = body['pago_id']

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('t_pagos')

    response = table.get_item(
        Key={
            'tenant_id': tenant_id,
            'pago_id': pago_id
        }
    )

    if 'Item' in response:
        return {
            'statusCode': 200,
            'body': json.dumps(response['Item'])
        }
    else:
        return {
            'statusCode': 404,
            'body': json.dumps({'message': 'Pago not found'})
        }
