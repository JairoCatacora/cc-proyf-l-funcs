import boto3
import json

def lambda_handler(event, context):
    try:
        query_params = event.get('queryStringParameters', {})
        product_name = query_params.get('product_name')
        product_brand = query_params.get('product_brand')

        if not product_name and not product_brand:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Debe proporcionar product_name o product_brand para la búsqueda'})
            }

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('pf_pagos')

        filter_expression = []
        expression_attribute_values = {}

        if product_name:
            filter_expression.append('product_name = :product_name')
            expression_attribute_values[':product_name'] = product_name

        if product_brand:
            filter_expression.append('product_brand = :product_brand')
            expression_attribute_values[':product_brand'] = product_brand

        filter_expression = " AND ".join(filter_expression)

        response = table.scan(
            FilterExpression=filter_expression,
            ExpressionAttributeValues=expression_attribute_values
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
