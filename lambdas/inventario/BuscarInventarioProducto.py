import boto3
import json

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('t_inventarios')

    tenant_id = event['pathParameters']['tenant_id']
    product_id = event['pathParameters']['product_id']

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
            'body': json.dumps({'error': 'Producto no fue encontrado en el inventario'})
        }
    
