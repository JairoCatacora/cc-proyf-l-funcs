import boto3
import json

def lambda_handler(event, context):
    # Extraer los datos del body de la solicitud
    body = json.loads(event['body'])
    tenant_id = body['tenant_id']
    order_id = body['order_id']
    order_status = body['order_status']
    
    # Aquí deberías tener una validación para comprobar que el tenant_id está autorizado
    # Por ejemplo, si tienes una lista de tenants autorizados o un sistema de autenticación
    authorized_tenant_id = 'some_authorized_tenant_id'  # Este valor debe ser dinámico o autenticado

    # Validar que el tenant_id del body sea el mismo que el autorizado
    if tenant_id != authorized_tenant_id:
        return {
            'statusCode': 403,  # Forbidden
            'body': json.dumps({'message': 'Unauthorized tenant_id'})
        }

    # Conectar a DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('t_orders')

    # Actualizar el estado de la orden en DynamoDB
    try:
        # Actualizar la orden
        response = table.update_item(
            Key={
                'order_id': order_id
            },
            UpdateExpression="set order_status = :order_status",
            ExpressionAttributeValues={
                ':order_status': order_status
            },
            ReturnValues="UPDATED_NEW"
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Order status updated successfully', 'updated': response['Attributes']})
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': f'Error updating order: {str(e)}'})
        }
