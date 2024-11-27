import boto3
from decimal import Decimal
from datetime import datetime, timedelta
import urllib3
import json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('pf_ordenes')
http = urllib3.PoolManager()

def lambda_handler(event, context):
    try:
        tenant_id = event['body']['tenant_id']
        order_id = event['body']['order_id']
        user_id = event['body']['user_id']
        user_info = event['body']['user_info']
        product_list = event['body']['products']
        creation_date = datetime.now()
        shipping_date = creation_date + timedelta(days=7)

        if not product_list:
            return {
                "statusCode": 400,
                "body": {"message": "La lista de productos no puede estar vacía."}
            }

        total_price = Decimal(0)
        for product in product_list:
            product_id = product['product_id']
            quantity = Decimal(product['quantity'])

            url = f"https://3j1d1u98t7.execute-api.us-east-1.amazonaws.com/dev/product/search?tenant_id={tenant_id}&product_id={product_id}"
            response = http.request('GET', url)

            if response.status != 200:
                return {
                    "statusCode": 404,
                    "body": {"message": f"No se encontró información para el producto con ID {product_id}"}
                }

            product_data = json.loads(response.data.decode('utf-8'))['body']
            price = Decimal(str(product_data['product_price']))
            total_price += price * quantity

        table.put_item(
            Item={
                "tenant_id": tenant_id,
                "order_id" : order_id,
                "user_id": user_id,
                "user_info": user_info,
                "creation_date": creation_date.isoformat(),
                "shipping_date": shipping_date.isoformat(),
                'order_status': 'PENDING',
                "products": product_list,
                "total_price": total_price
            }
        )

        return {
            "statusCode": 201,
            "body": {"message": "Orden creada exitosamente", "order_id": order_id, "total_price": float(total_price)}
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": {"message": "Error al crear la orden", "error": str(e)}
        }
