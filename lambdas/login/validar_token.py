import boto3
from datetime import datetime

def lambda_handler(event, context):
    # Entrada (json)
    auth_header = event['headers']['Authorization']
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return {
            'statusCode': 400,
            'body': 'Authorization header inválido o no presente'
        }
    
    token = auth_header.split(' ')[1]
    
    # Conexión a DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('t_tokens_acceso')
    
    # Buscar el token en la tabla
    try:
        response = table.get_item(Key={'token': token})
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Error al consultar la base de datos: {str(e)}'
        }
    
    if 'Item' not in response:
        return {
            'statusCode': 403,
            'body': 'Token no existe'
        }
    
    # Validar si el token está expirado
    token_data = response['Item']
    expires = datetime.strptime(token_data['expires'], '%Y-%m-%d %H:%M:%S')
    now = datetime.now()
    
    if now > expires:
        return {
            'statusCode': 403,
            'body': 'Token expirado'
        }
    
    # Token válido
    return {
        'statusCode': 200,
        'body': 'Token válido'
    }