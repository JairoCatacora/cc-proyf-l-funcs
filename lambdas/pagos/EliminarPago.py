import boto3
import json
import requests

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('pf_pagos')

def validate_token(token):
    url = "https://0w7xbgvz6f.execute-api.us-east-1.amazonaws.com/test/token/validate"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    try:
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            return response.json() 
        else:
            raise Exception(response.json().get('error', 'Token no válido'))
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error en la validación del token: {str(e)}")

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
