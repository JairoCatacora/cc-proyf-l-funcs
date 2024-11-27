import boto3
import json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('pf_ordenes')

def lambda_handler(event, context):
    try:
        user_id = event['query']['user_id']
        order_id = event['query']['order_id']

        if not user_id or not order_id:
            return {
                'statusCode': 400,
                'body': {'message': 'user_id y order_id son requeridos.'}
            }

        response = table.query(
            IndexName='user_id-order_id-index',
            KeyConditionExpression=Key('user_id').eq(user_id) & Key('order_id').eq(order_id)
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
