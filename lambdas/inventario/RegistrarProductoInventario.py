import boto3
import json

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('t_inventarios')

    tenant_id = event.get('tenant_id')
    product_id = event.get('product_id')
    inventario_info = event.get('inventario_info')

    if not (tenant_id and product_id and inventario_info):
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid request body'})
        }

    table.put_item(
        Item={
            'tenant_id': tenant_id,
            'product_id': product_id,
            'inventario_info': inventario_info
        }
    )

    return {
        'statusCode': 201,
        'body': json.dumps({
            'message': 'Producto agregado al inventario',
            'tenant_id': tenant_id,
            'product_id': product_id,
            'inventario_info': inventario_info
        })
    }
