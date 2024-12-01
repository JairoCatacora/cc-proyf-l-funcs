import boto3
from datetime import datetime
import json

def lambda_handler(event, context):
    auth_header = event.get('headers', {}).get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return {
            'statusCode': 400,
            'body': {'error': 'Encabezado Authorization inválido o ausente'}
        }

    token = auth_header.split(' ')[1]

    dynamodb = boto3.resource('dynamodb')
    token_table = dynamodb.Table('t_tokens_acceso')

    try:
        response = token_table.get_item(Key={'token': token})
        token_item = response.get('Item')
    except Exception as e:
        return {
            'statusCode': 500,
            'body': {'error': 'Error al consultar DynamoDB', 'details': str(e)}
        }

    if not token_item:
        return {
            'statusCode': 403,
            'body': {'error': 'Token no existe'}
        }

    expiration_time = datetime.strptime(token_item['expires'], '%Y-%m-%d %H:%M:%S')
    if datetime.now() > expiration_time:
        return {
            'statusCode': 403,
            'body': {'error': 'Token expirado'}
        }

    return {
        'statusCode': 200,
        'body': {'message': 'Token válido'}
    }