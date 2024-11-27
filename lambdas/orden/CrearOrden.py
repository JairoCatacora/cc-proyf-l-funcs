import boto3
import json
import requests

def lambda_handler(event, context):
    tenant_id = event['body']['tenant_id']
    order_id = event['body']['order_id']
    user_id = event['body']['user_id']
    products = event['body']['products']
    
    try:
        payload = {
            "tenant_id": tenant_id,
            "user_id": user_id,
            "products": products
        }
        lambda_client = boto3.client('lambda')
        response = lambda_client.invoke(
            FunctionName='create_payment',
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )
        payment_response = json.loads(response['Payload'].read())
        
        if payment_response['statusCode'] != 201:
            raise Exception(f"Error en la creación del pago: {payment_response['body']}")
        
        payment_data = json.loads(payment_response['body'])
        payment_id = payment_data['payment_id']
        payment_total = payment_data['total']

        dynamodb = boto3.resource('dynamodb')
        orders_table = dynamodb.Table('pf_ordenes')

        order_item = {
            'tenant_id': tenant_id,
            'order_id': order_id,
            'user_id': user_id,
            'products': products,
            'payment_id': payment_id,
            'payment_total': payment_total,
            'user_info': payment_data['user_info'], 
            'timestamp': datetime.datetime.utcnow().isoformat()
        }

        orders_table.put_item(Item=order_item)

        return {
            'statusCode': 201,
            'body': {'message': 'Order created successfully', 'order_id': order_id}
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': {'message': f'Error al crear la orden: {str(e)}'}
        }
