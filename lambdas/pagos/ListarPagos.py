import boto3
import json
from boto3.dynamodb.conditions import Key
import requests

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

    tenant_id = event['query']['tenant_id']
    user_id = event['query']['user_id']

    if not tenant_id and not user_id:
        return {
            'statusCode': 400,
            'body': {'message': 'Se debe proporcionar tenant_id, user_id o ambos para listar los pagos.'}
        }

    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('pf_pagos')
        
        response = table.query(
            IndexName='tenant_id-user_id-index',
            KeyConditionExpression=Key('tenant_id').eq(tenant_id) & Key('user_id').eq(user_id)
        )

        pagos = response.get('Items', [])

        if pagos:
            return {
                'statusCode': 200,
                'body': {
                    'message': 'Pagos encontrados',
                    'pagos': pagos
                }
            }
        else:
            return {
                'statusCode': 404,
                'body': {'message': 'No se encontraron pagos con los criterios proporcionados.'}
            }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': {'message': f'Error al listar pagos: {str(e)}'}
        }
