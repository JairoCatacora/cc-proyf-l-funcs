import boto3
import json
import requests

def lambda_handler(event, context):
    tenant_id = event['body']['tenant_id']
    user_id = event['body']['user_id']
    
    # Llamada al microservicio de pagos para obtener la dirección y teléfono del usuario
    try:
        user_response = requests.get(f'https://api.example.com/users/{user_id}')
        user_data = user_response.json()
        user_address = user_data['user_address']
        user_phone = user_data['user_phone']
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': f'Error fetching user data: {str(e)}'})
        }

    # Llamada al microservicio de productos para obtener el nombre y el precio del producto
    try:
        product_response = requests.get(f'https://api.example.com/products/{user_id}')
        product_data = product_response.json()
        product_name = product_data['product_name']
        product_price = product_data['product_price']
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': f'Error fetching product data: {str(e)}'})
        }

    # Conectar a DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('t_orders')

    # Consultar órdenes en DynamoDB usando tenant_id y user_id
    try:
        response = table.query(
            KeyConditionExpression='tenant_id = :tenant_id',
            FilterExpression='user_id = :user_id',
            ExpressionAttributeValues={
                ':tenant_id': tenant_id,
                ':user_id': user_id
            }
        )

        # Si hay órdenes, agregamos la información adicional y las devolvemos
        if response['Items']:
            for order in response['Items']:
                order['user_address'] = user_address
                order['user_phone'] = user_phone
                order['product_name'] = product_name
                order['product_price'] = product_price

            return {
                'statusCode': 200,
                'body': json.dumps(response['Items'])
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'No orders found for this user'})
            }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': f'Error fetching orders: {str(e)}'})
        }
