import boto3
import json

def lambda_handler(event, context):
    tenant_id = event['query'].get('tenant_id')
    user_id = event['query'].get('user_id')

    if not tenant_id and not user_id:
        return {
            'statusCode': 400,
            'body': {'message': 'Se debe proporcionar tenant_id, user_id o ambos para listar los pagos.'}
        }

    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('pf_pagos')

        filter_expression = []
        expression_attribute_values = {}

        if tenant_id:
            filter_expression.append('tenant_id = :tenant_id')
            expression_attribute_values[':tenant_id'] = tenant_id

        if user_id:
            filter_expression.append('user_id = :user_id')
            expression_attribute_values[':user_id'] = user_id

        filter_expression = " AND ".join(filter_expression)

        response = table.scan(
            FilterExpression=filter_expression,
            ExpressionAttributeValues=expression_attribute_values
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
