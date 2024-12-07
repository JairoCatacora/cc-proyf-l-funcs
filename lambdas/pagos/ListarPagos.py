import boto3
import json
from boto3.dynamodb.conditions import Key
import urllib3

def validate_token(token):
    url = "https://i1w2t4axo8.execute-api.us-east-1.amazonaws.com/prod/token/validate"
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

        if not tenant_id or not user_id:
            return {
                'statusCode': 400,
                'body': {'message': 'user_id y order_id son requeridos.'}
            }

        response = table.query(
            IndexName='tenant_id-user_id-index',
            KeyConditionExpression=Key('tenant_id').eq(tenant_id) & Key('user_id').eq(user_id)
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