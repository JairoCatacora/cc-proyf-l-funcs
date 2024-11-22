import boto3
import json

def lambda_handler(event, context):
    # Obtener los parámetros de búsqueda desde la query string
    producto_nombre = event['queryStringParameters'].get('product_name', None)
    producto_marca = event['queryStringParameters'].get('product_brand', None)
    
    if not producto_nombre and not producto_marca:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Se debe proporcionar un nombre de producto o una marca para la búsqueda'})
        }

    # Configurar DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('t_pagos')

    # Construir la expresión de filtro
    filter_expression = []
    expression_attribute_values = {}

    if producto_nombre:
        filter_expression.append('producto_nombre = :producto_nombre')
        expression_attribute_values[':producto_nombre'] = producto_nombre

    if producto_marca:
        filter_expression.append('producto_marca = :producto_marca')
        expression_attribute_values[':producto_marca'] = producto_marca

    # Si hay más de una condición, unirlas con "AND"
    filter_expression = " AND ".join(filter_expression)

    # Realizar la consulta en DynamoDB
    try:
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
                'body': json.dumps({
                    'message': 'No se encontraron pagos con ese nombre de producto o marca'
                })
            }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f'Error al buscar pagos: {str(e)}'
            })
        }
