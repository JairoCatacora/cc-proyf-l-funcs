import boto3
import json
from boto3.dynamodb.conditions import Key
import urllib3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('pf_ordenes')

def validate_token(token):
    url = "https://bfh1meojk2.execute-api.us-east-1.amazonaws.com/prod/token/validate"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    http = urllib3.PoolManager()
    response = http.request("POST", url, headers=headers)
    
    if response.status == 200:
        return json.loads(response.data.decode('utf-8'))
    else:
        error_msg = json.loads(response.data.decode('utf-8')).get('error', 'Token no válido')
        raise Exception(error_msg)

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

        tenant_id = event['query']['tenant_id']
        user_id = event['query']['user_id']
        order_id = event['query']['order_id']

        tu_id = f'{tenant_id}#{user_id}'

        if not user_id or not order_id:
            return {
                'statusCode': 400,
                'body': {'message': 'user_id y order_id son requeridos.'}
            }

        response = table.query(
            IndexName='tu_id-order_id-index',
            KeyConditionExpression=Key('tu_id').eq(tu_id) & Key('order_id').eq(order_id)
        )

        return {
            'statusCode': 200,
            'body': {
                'message': 'Órdenes listadas exitosamente',
                'orders': response.get('Items', [])
            }
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': {'message': f'Error al listar órdenes: {str(e)}'}
        }
