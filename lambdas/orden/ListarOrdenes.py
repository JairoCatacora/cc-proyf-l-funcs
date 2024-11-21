import boto3
import json

def lambda_handler(event, context):
    body = json.loads(event['body'])
    tenant_id = body['tenant_id']
    user_id = body['user_id']

    dynamodb = boto3.resource('dynamodb')
    orders_table = dynamodb.Table('t_orders')
    products_table = dynamodb.Table('t_productos')

    response = orders_table.query(
        KeyConditionExpression='tenant_id = :tenant_id',
        FilterExpression='user_id = :user_id',
        ExpressionAttributeValues={
            ':tenant_id': tenant_id,
            ':user_id': user_id
        }
    )

    orders = response.get('Items', [])

    for order in orders:
        if 'order_info' in order and 'lista_productos' in order['order_info']:
            for producto in order['order_info']['lista_productos']:
                producto_id = producto['producto_id']

                product_response = products_table.get_item(
                    Key={
                        'tenant_id': tenant_id,
                        'producto_id': producto_id
                    }
                )

                if 'Item' in product_response:
                    producto['product_info'] = {
                        'name': product_response['Item'].get('name'),
                        'category': product_response['Item'].get('category'),
                        'price': product_response['Item'].get('price'),
                        'image': product_response['Item'].get('image'),
                        'detalles': product_response['Item'].get('detalles', {})
                    }

    return {
        'statusCode': 200,
        'body': json.dumps(orders if orders else {'message': 'No orders found for this user'})
    }
