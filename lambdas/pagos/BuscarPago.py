import boto3
import json

def lambda_handler(event, context):
    try:
        user_id = event['query']['user_id']
        pago_id = event['query']['pago_id']

        if not user_id and not pago_id:
            return {
                'statusCode': 400,
                'body': {'message': 'Debe proporcionar product_name o product_brand para la búsqueda'}
            }

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('pf_pagos')

        response = table.query(
            IndexName='user_id-pago_id-index',
            KeyConditionExpression=Key('user_id').eq(user_id) & Key('pago_id').eq(pago_id)
        )

        pagos = response.get('Items', [])

        if pagos:
            return {
                'statusCode': 200,
                'body': {'message': 'Pagos encontrados', 'pagos': pagos}
            }
        else:
            return {
                'statusCode': 404,
                'body': {'message': 'No se encontraron pagos con los criterios dados'}
            }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': {'message': f'Error buscando pagos: {str(e)}'}
        }
