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
            
        user_id = event['query']['user_id']
        pago_id = event['query']['pago_id']

        if not user_id and not pago_id:
            return {
                'statusCode': 400,
                'body': {'message': 'Debe proporcionar product_name o product_brand para la búsqueda'}
            }

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('pf_pagos')

        response = table.query(
            IndexName='user_id-pago_id-index',
            KeyConditionExpression=Key('user_id').eq(user_id) & Key('pago_id').eq(pago_id)
        )

        pagos = response.get('Items', [])

        if pagos:
            return {
                'statusCode': 200,
                'body': {'message': 'Pagos encontrados', 'pagos': pagos}
            }
        else:
            return {
                'statusCode': 404,
                'body': {'message': 'No se encontraron pagos con los criterios dados'}
            }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': {'message': f'Error buscando pagos: {str(e)}'}
        }
