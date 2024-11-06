import boto3
import json

def lambda_handler(event, context):
    tenant_id = event['body']['tenant_id']
    order_id = event['body']['order_id']
    order_info = event['body']['order_info']

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('t_orders')
    response = table.update_item(
        Key={
            'tenant_id': tenant_id,
            'order_id': order_id
        },
        UpdateExpression='SET order_info = :info',
        ExpressionAttributeValues={
            ':info': order_info
        },
        ReturnValues='UPDATED_NEW'
    )

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Order updated successfully',
            'updatedAttributes': response['Attributes']
        })
    }
