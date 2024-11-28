import boto3
import json

def lambda_handler(event, context):
    tenant_id = event['query']['tenant_id']
    user_id = event['query']['user_id']

    if not tenant_id and not user_id:
        return {
            'statusCode': 400,
            'body': {'message': 'Se debe proporcionar tenant_id, user_id o ambos para listar los pagos.'}
        }

    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('pf_pagos')
        
        response = table.query(
            IndexName='tenant_id-user_id-index',
            KeyConditionExpression=Key('tenant_id').eq(tenant_id) & Key('user_id').eq(user_id)
        )

        pagos = response.get('Items', [])

        if pagos:
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Pagos encontrados',
                    'pagos': pagos
                })
            }
        else:
            return {
                'statusCode': 404,
                'body': {'message': 'No se encontraron pagos con los criterios proporcionados.'}
            }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': {'message': f'Error al listar pagos: {str(e)}'}
        }
