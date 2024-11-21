import boto3
import json

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('t_productos')

    # Extraer datos del cuerpo del evento
    body = event['body']
    tenant_id = body.get('tenant_id')
    product_id = body.get('product_id')
    product_name = body.get('product_name')

    # Validar que se proporciona un tenant_id
    if not tenant_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'tenant_id is required'})
        }

    # Búsqueda por tenant_id y product_id
    if product_id:
        response = table.get_item(
            Key={
                'tenant_id': tenant_id,
                'product_id': product_id
            }
        )

        if 'Item' in response:
            return {
                'statusCode': 200,
                'body': json.dumps(response['Item'])
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Product not found'})
            }

    # Búsqueda por tenant_id y product_name (si no se proporciona product_id)
    elif product_name:
        response = table.scan(
            FilterExpression='tenant_id = :tenant_id AND product_name = :product_name',
            ExpressionAttributeValues={
                ':tenant_id': tenant_id,
                ':product_name': product_name
            }
        )

        if response['Items']:
            return {
                'statusCode': 200,
                'body': json.dumps(response['Items'])
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Product not found'})
            }

    # Si no se proporciona ni product_id ni product_name
    else:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Either product_id or product_name must be provided'})
        }
