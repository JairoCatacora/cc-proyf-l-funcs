import boto3
import json

def lambda_handler(event, context):
    body = json.loads(event['body'])
    tenant_id = body['tenant_id']
    order_id = body['order_id']

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('t_orders')

    response = table.get_item(
        Key={
            'tenant_id': tenant_id,
            'order_id': order_id
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
            'body': json.dumps({'message': 'Order not found'})
        }
