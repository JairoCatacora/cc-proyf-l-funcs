import boto3
import json
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('pf_ordenes')

def lambda_handler(event, context):
    try:
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
