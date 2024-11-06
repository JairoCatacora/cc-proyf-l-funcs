import boto3
import json

def lambda_handler(event, context):
    tenant_id = event['body']['tenant_id']
    user_id = event['body']['user_id']

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('t_orders')

    response = table.query(
        KeyConditionExpression='tenant_id = :tenant_id',
        FilterExpression='user_id = :user_id',
        ExpressionAttributeValues={
            ':tenant_id': tenant_id,
            ':user_id': user_id
        }
    )

    return {
        'statusCode': 200,
        'body': json.dumps(response['Items'] if response['Items'] else {'message': 'No orders found for this user'})
    }