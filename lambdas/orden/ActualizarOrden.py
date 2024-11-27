import boto3
import json

def lambda_handler(event, context):
    try:
        tenant_id = event['body']['tenant_id']
        order_id = event['body']['order_id']
        estado = event['body']['order_status']

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('pf_ordenes')

        response = table.update_item(
            Key={
                'tenant_id': tenant_id,
                'order_id': order_id
            },
            UpdateExpression="SET estado = :estado",
            ExpressionAttributeValues={
                ':estado': estado
            },
            ReturnValues="UPDATED_NEW"
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Order status updated successfully', 'updated': response['Attributes']})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': f'Error updating order: {str(e)}'})
        }
