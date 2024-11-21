import boto3
import json

def lambda_handler(event, context):
    try:
        # Obtener la lista de productos desde el evento
        productos = event.get('body', {}).get('productos', [])

        # Validar que la lista no esté vacía
        if not isinstance(productos, list) or not productos:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid request: missing or invalid productos list'})
            }
        
        # Inicializar la conexión a DynamoDB
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('t_productos')
        
        # Lista para almacenar el resultado de cada registro
        resultados = []

        # Procesar cada producto en la lista
        for producto in productos:
            tenant_id = producto.get('tenant_id')
            producto_id = producto.get('producto_id')
            product_info = producto.get('product_info')

            # Validar que todos los campos necesarios estén presentes
            if tenant_id and producto_id and product_info:
                try:
                    # Insertar el producto en la tabla DynamoDB
                    table.put_item(
                        Item={
                            'tenant_id': tenant_id,
                            'producto_id': producto_id,
                            'product_info': product_info
                        }
                    )

                    # Añadir un mensaje de éxito para este producto
                    resultados.append({
                        'tenant_id': tenant_id,
                        'producto_id': producto_id,
                        'message': 'Product created successfully'
                    })
                except Exception as e:
                    # Capturar errores específicos para cada producto
                    resultados.append({
                        'tenant_id': tenant_id,
                        'producto_id': producto_id,
                        'error': str(e)
                    })
            else:
                # Si faltan datos, registrar un error
                resultados.append({
                    'tenant_id': tenant_id,
                    'producto_id': producto_id,
                    'error': 'Missing required fields'
                })

        # Devolver el resumen de resultados
        return {
            'statusCode': 201,
            'body': json.dumps(resultados)
        }

    except Exception as e:
        print("Exception:", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
