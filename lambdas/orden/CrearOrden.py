import boto3
from decimal import Decimal
from datetime import datetime, timedelta
import json

dynamodb = boto3.resource('dynamodb')
orders_table = dynamodb.Table('pf_ordenes')
inventory_table = dynamodb.Table('pf_inventario')
products_table = dynamodb.Table('pf_productos')

def search_product(tenant_id, product_id=None, product_name=None):
    try:
        if not tenant_id:
            return {
                "statusCode": 400,
                "body": {"message": "tenant_id is required"}
            }

        if product_id:
            response = products_table.get_item(Key={'tenant_id': tenant_id, 'product_id': product_id})
            item = response.get('Item')
            if item:
                return {"statusCode": 200, "body": item}
            else:
                return {"statusCode": 404, "body": {"message": "Product not found"}}

        if product_name:
            response = products_table.scan(
                FilterExpression="tenant_id = :tenant_id AND product_name = :product_name",
                ExpressionAttributeValues={
                    ":tenant_id": tenant_id,
                    ":product_name": product_name
                }
            )
            items = response.get('Items', [])
            if items:
                return {"statusCode": 200, "body": items}
            else:
                return {"statusCode": 404, "body": {"message": "Product not found"}}

        return {"statusCode": 400, "body": {"message": "Either product_id or product_name must be provided"}}
    except Exception as e:
        return {"statusCode": 500, "body": {"error": str(e)}}

def update_inventory(tenant_id, inventory_id, product_id, cantidad, observaciones, add):
    try:
        last_modification = datetime.utcnow().isoformat()

        response = inventory_table.get_item(
            Key={'tenant_id': tenant_id, 'ip_id': f"{inventory_id}#{product_id}"}
        )
        current_item = response.get('Item')
        if not current_item:
            return {"statusCode": 404, "body": {"message": "Item not found in inventory"}}

        current_stock = current_item['stock']
        if not add and current_stock < cantidad:
            return {
                "statusCode": 400,
                "body": {"message": "Insufficient stock to remove the requested quantity"}
            }

        new_stock = current_stock + cantidad if add else current_stock - cantidad
        inventory_table.update_item(
            Key={'tenant_id': tenant_id, 'ip_id': f"{inventory_id}#{product_id}"},
            UpdateExpression="""
                SET stock = :new_stock,
                    observaciones = :observaciones,
                    last_modification = :last_modification
            """,
            ExpressionAttributeValues={
                ':new_stock': new_stock,
                ':observaciones': observaciones,
                ':last_modification': last_modification
            },
            ReturnValues="UPDATED_NEW"
        )
        return {"statusCode": 200, "body": {"message": "Stock updated successfully"}}
    except Exception as e:
        return {"statusCode": 500, "body": {"error": str(e)}}

def lambda_handler(event, context):
    try:
        print("Evento recibido:", event)
        
        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        tenant_id = body['tenant_id']
        order_id = body['order_id']
        user_id = body['user_id']
        user_info = body['user_info']
        product_list = body['products']
        inventory_id = body['inventory_id']
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

            product_response = search_product(tenant_id, product_id)
            if product_response["statusCode"] != 200:
                return {
                    "statusCode": 404,
                    "body": {"message": f"No se encontró información para el producto con ID {product_id}"}
                }
            product_data = product_response['body']
            price = Decimal(str(product_data['product_price']))

            inventory_response = update_inventory(
                tenant_id=tenant_id,
                inventory_id=inventory_id,
                product_id=product_id,
                cantidad=int(quantity),
                observaciones="venta",
                add=False
            )
            if inventory_response["statusCode"] != 200:
                return {
                    "statusCode": 404,
                    "body": {"message": f"No se pudo actualizar el stock para el producto con ID {product_id}"}
                }

            total_price += price * quantity

        orders_table.put_item(
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
                "total_price": Decimal(str(total_price))
            }
        )

        return {
            "statusCode": 201,
            "body": {
                "message": "Orden creada exitosamente",
                "order_id": order_id,
                "total_price": Decimal(str(total_price))
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
