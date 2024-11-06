import boto3
import json

def lambda_handler(event, context):
    tenant_id = event['body']['tenant_id']
    producto_id = event['body']['producto_id']
    product_info = event['body']['product_info']
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('t_productos')
    table.put_item(
        Item={
            'tenant_id': tenant_id,
            'producto_id': producto_id,
            'product_info': product_info
        }
    )

    return {
        'statusCode': 201,
        'body': json.dumps({'message': 'Product created successfully'})
    }
