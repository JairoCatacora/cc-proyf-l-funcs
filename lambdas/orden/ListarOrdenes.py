import boto3
import json

def lambda_handler(event, context):
    tenant_id = event['query'].get('tenant_id')
    user_id = event['query'].get('user_id')

    if not tenant_id or not user_id:
        return {
            'statusCode': 400,
            'body': {'message': 'tenant_id y user_id son requeridos.'}
        }

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('pf_ordenes')

    try:
        response = table.query(
            IndexName='OrdenesUsuarioIndex',
            KeyConditionExpression='tenant_id = :tenant_id AND user_id = :user_id',
            ExpressionAttributeValues={
                ':tenant_id': tenant_id,
                ':user_id': user_id
            }
        )

        return {
            'statusCode': 200,
            'body': response.get('Items', [])
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': {'message': f'Error al listar órdenes: {str(e)}'}
        }
