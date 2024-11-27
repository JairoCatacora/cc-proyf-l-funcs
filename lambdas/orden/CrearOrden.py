import json
import boto3
import requests
from datetime import datetime, timedelta

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('pf_ordenes')

def lambda_handler(event, context):
    try:
        tenant_id = event['body']['tenant_id']
        order_id = event['body']['order_id']
        user_info = event['body']['user_info']
        creation_date = datetime.now()
        shipping_date = creation_date + timedelta(days=7)
        product_list = event['body']['products'] 
        
        if not product_list:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "La lista de productos no puede estar vacía."})
            }
        
        total_price = 0
        for product in product_list:
            product_id = product['product_id']
            quantity = product['quantity']
  
            url = f"https://pfj6am2bx0.execute-api.us-east-1.amazonaws.com/dev/product/search"
            params = {
                "tenant_id": tenant_id,
                "product_id": product_id
            }
            response = requests.get(url, params=params)
            
            if response.status_code != 200:
                return {
                    "statusCode": 404,
                    "body": json.dumps({
                        "message": f"No se encontró información para el producto con ID {product_id}"
                    })
                }
            
            product_data = response.json()
            price = float(product_data['price'])
            total_price += price * quantity
        
        # Crear la orden en DynamoDB
        table.put_item(
            Item={
                "tenant_id": tenant_id,
                "order_id": order_id,
                "user_info": user_info,
                "creation_date": creation_date.isoformat(),
                "shipping_date": shipping_date.isoformat(),
                "products": product_list,
                "total_price": total_price
            }
        )
        
        return {
            "statusCode": 201,
            "body": json.dumps({
                "message": "Orden creada exitosamente",
                "order_id": order_id,
                "total_price": total_price
            })
        }
    
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Error al crear la orden",
                "error": str(e)
            })
        }
