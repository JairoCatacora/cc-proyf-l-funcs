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
        print("Evento recibido:", event)
        
        tenant_id = event['body']['tenant_id']
        order_id = event['body']['order_id']
        user_id = event['body']['user_id']
        user_info = event['body']['user_info']
        product_list = event['body']['products']
        inventory_id = event['body']['inventory_id']
        creation_date = datetime.now()
        shipping_date = creation_date + timedelta(days=7)

        if not (tenant_id and order_id and user_id and user_info and inventory_id and product_list):
            return {
                "statusCode": 400,
                "body": {"message": "Todos los parámetros deben estar presentes."}
            }

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
            print(f"Buscando producto con URL: {url}")
            
            response = http.request('GET', url)

            print(f"Respuesta del producto (Status: {response.status}): {response.data.decode('utf-8')}")

            if response.status != 200:
                return {
                    "statusCode": 404,
                    "body": {"message": f"No se encontró información para el producto con ID {product_id}"}
                }

            product_data = json.loads(response.data.decode('utf-8'))['body']
            price = Decimal(str(product_data['product_price']))

            url2 = f"https://3j1d1u98t7.execute-api.us-east-1.amazonaws.com/dev/inventory/update"
            print(f"Actualizando inventario con URL: {url2}")

            info = {
                "tenant_id": tenant_id,
                "inventory_id": inventory_id,
                "product_id": product_id,
                "cantidad": int(quantity),
                "observaciones": "venta",
                "add": False
            }
            encoded_body = json.dumps(info)

            print(f"Payload para actualizar inventario: {encoded_body}")

            response2 = http.request(
                "PATCH",
                url2,
                body=encoded_body,
                headers={'Content-Type': 'application/json'}
            )

            print(f"Respuesta de inventario (Status: {response2.status}): {response2.data.decode('utf-8')}")

            if response2.status != 200:
                return {
                    "statusCode": 404,
                    "body": {"message": f"No se pudo actualizar el stock para el producto con ID {product_id}"}
                }

            total_price += price * quantity

        print("Guardando la orden en DynamoDB con datos:")
        print({
            "tenant_id": tenant_id,
            "order_id": order_id,
            "user_id": user_id,
            "user_info": user_info,
            "inventory_id": inventory_id,
            "creation_date": creation_date.isoformat(),
            "shipping_date": shipping_date.isoformat(),
            "order_status": "PENDING",
            "products": product_list,
            "total_price": float(total_price)
        })

        table.put_item(
            Item={
                "tenant_id": tenant_id,
                "order_id": order_id,
                "user_id": user_id,
                "user_info": user_info,
                "inventory_id": inventory_id,
                "creation_date": creation_date.isoformat(),
                "shipping_date": shipping_date.isoformat(),
                "order_status": "PENDING",
                "products": product_list,
                "total_price": float(total_price)
            }
        )

        return {
            "statusCode": 201,
            "body":{
                "message": "Orden creada exitosamente",
                "order_id": order_id,
                "total_price": float(total_price)
            }
        }

    except Exception as e:
        print("Error en el procesamiento:", str(e))
        return {
            "statusCode": 500,
            "body": {
                "message": "Error al crear la orden",
                "error": str(e)
            }
        }
