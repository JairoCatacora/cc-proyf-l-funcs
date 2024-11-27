import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('pf_ordenes')

def lambda_handler(event, context):
    try:
        tenant_id = event['body']['tenant_id']
        order_id = event['body']['order_id']
        order_status = event['body']['order_status']

        response = table.update_item(
            Key={
                "tenant_id": tenant_id,
                "#order_id": order_id
            },
            UpdateExpression="SET order_status = :status",
            ExpressionAttributeValues={
                ":status": order_status
            },
            ReturnValues="UPDATED_NEW"
        )

        return {
            "statusCode": 200,
            "body": {"message": "Estado de la orden actualizado", "updated": response['Attributes']}
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": {"message": "Error al actualizar la orden", "error": str(e)}
        }
