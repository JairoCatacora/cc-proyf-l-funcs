import boto3
import json

def lambda_handler(event, context):
    # Obtener el recurso de DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('t_inventarios')

    # Verificar si el evento tiene el cuerpo esperado
    body = event.get('body')
    if not body:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing request body'})
        }

    # Parsear el cuerpo (si está en formato JSON string)
    if isinstance(body, str):
        body = json.loads(body)

    # Obtener la lista de inventarios
    inventarios = body.get('inventarios')
    if not isinstance(inventarios, list) or not inventarios:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid or missing inventarios list'})
        }

    resultados = []

    # Procesar cada item en la lista
    for inventario in inventarios:
        tenant_id = inventario.get('tenant_id')
        product_id = inventario.get('product_id')
        inventario_info = inventario.get('inventario_info')

        # Validar que todos los campos requeridos estén presentes
        if not (tenant_id and product_id and inventario_info):
            resultados.append({
                'tenant_id': tenant_id,
                'product_id': product_id,
                'error': 'Missing required fields'
            })
            continue

        # Crear el objeto para insertar en DynamoDB
        try:
            table.put_item(
                Item={
                    'tenant_id': tenant_id,
                    'product_id': product_id,
                    'inventario_info': inventario_info
                }
            )
            resultados.append({
                'tenant_id': tenant_id,
                'product_id': product_id,
                'message': 'Producto agregado al inventario'
            })
        except Exception as e:
            resultados.append({
                'tenant_id': tenant_id,
                'product_id': product_id,
                'error': str(e)
            })

    # Devolver el resultado de las operaciones
    return {
        'statusCode': 201,
        'body': json.dumps(resultados)
    }
