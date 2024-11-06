import boto3
import json

def lambda_handler(event, context):
    tenant_id = event['body']['tenant_id']
    producto_id = event['body']['producto_id']
    
    #Faltan los filtros de busqueda - Search by - Filter by

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('t_productos')
    response = table.get_item(
        Key={
            'tenant_id': tenant_id,
            'producto_id': producto_id
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
