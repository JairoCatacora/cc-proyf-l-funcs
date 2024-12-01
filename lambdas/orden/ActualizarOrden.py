import boto3
import requests

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('pf_ordenes')

def validate_token(token):
    url = "https://0w7xbgvz6f.execute-api.us-east-1.amazonaws.com/test/token/validate"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    try:
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            return response.json() 
        else:
            raise Exception(response.json().get('error', 'Token no válido'))
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error en la validación del token: {str(e)}")

def lambda_handler(event, context):
    try:
        token = event.get('headers', {}).get('Authorization', '').split(' ')[1] if 'Authorization' in event.get('headers', {}) else None
        if not token:
            return {
                'statusCode': 400,
                'body': { "message": "Token is required" }
            }
        try:
            validate_token(token)
        except Exception as error:
            return {
                'statusCode': 403,
                'body': { "message": str(error) }
            }

        tenant_id = event['body']['tenant_id']
        order_id = event['body']['order_id']
        order_status = event['body']['order_status']

        response = table.update_item(
            Key={
                "tenant_id": tenant_id,
                "order_id": order_id
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
