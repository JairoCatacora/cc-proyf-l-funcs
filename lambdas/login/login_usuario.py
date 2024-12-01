import boto3
import hashlib
import uuid
from datetime import datetime, timedelta
import json

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def lambda_handler(event, context):
    tenant_id = ['body']['tenant_id']
    user_id = ['body']['user_id']
    password = ['body']['password']

    if not tenant_id or not user_id or not password:
        return {
            'statusCode': 400,
            'body': {'error': 'Faltan parámetros requeridos'}
        }

    dynamodb = boto3.resource('dynamodb')
    user_table = dynamodb.Table('pf_usuarios')

    try:
        response = user_table.get_item(Key={'tenant_id': tenant_id, 'user_id': user_id})
        user = response.get('Item')
    except Exception as e:
        return {
            'statusCode': 500,
            'body': {'error': 'Error al consultar DynamoDB', 'details': str(e)}
        }

    if not user:
        return {
            'statusCode': 403,
            'body': {'error': 'Usuario no existe'}
        }

    hashed_password = hash_password(password)
    if hashed_password != user['password']:
        return {
            'statusCode': 403,
            'body': {'error': 'Contraseña incorrecta'}
        }

    token = str(uuid.uuid4())
    expiration_time = datetime.now() + timedelta(minutes=60)
    token_item = {
        'token': token,
        'tenant_id': tenant_id,
        'user_id': user_id,
        'expires': expiration_time.strftime('%Y-%m-%d %H:%M:%S')
    }

    token_table = dynamodb.Table('t_tokens_acceso')
    try:
        token_table.put_item(Item=token_item)
    except Exception as e:
        return {
            'statusCode': 500,
            'body': {'error': 'Error al guardar el token', 'details': str(e)}
        }

    return {
        'statusCode': 200,
        'body': {'token': token}
    }
