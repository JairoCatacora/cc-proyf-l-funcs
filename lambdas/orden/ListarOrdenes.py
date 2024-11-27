import boto3
import json

# Inicializar recurso de DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('pf_ordenes')

def lambda_handler(event, context):
    try:
        tenant_id = event['query'].get('tenant_id')
        user_id = event['query'].get('user_id')

        if not tenant_id or not user_id:
            return {
                'statusCode': 400,
                'body': {'message': 'tenant_id y user_id son requeridos.'}
            }

        response = table.query(
            IndexName='tenant_id-user_id-index', 
            KeyConditionExpression='tenant_id = :tenant_id AND user_id = :user_id',
            ExpressionAttributeValues={
                ':tenant_id': tenant_id,
                ':user_id': user_id
            }
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
