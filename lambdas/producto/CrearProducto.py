import boto3
import json

def lambda_handler(event, context):
    tenant_id = event['body']['tenant_id']
    product_id = event['body']['product_id']
    product_name = event['body']['product_name']
    product_brand = event['body']['product_brand']
    product_info = event['body']['product_info']
    product_price = Decimal(str(event['body']['product_price']))
    product_stock = int(event['body']['product_stock'])
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('t_productos')
    table.put_item(
        Item={
            'tenant_id': tenant_id,
            'product_id': product_id,
            'product_name': product_name,
            'product_brand': product_brand,
            'product_info': product_info,
            'product_price': product_price,
            'product_stock': product_stock
        }
    )

    return {
        'statusCode': 201,
        'body': json.dumps({'message': 'Product created successfully'})
    }
