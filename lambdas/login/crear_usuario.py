import boto3
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def lambda_handler(event, context):
    try:
        tenant_id = event['body']['tenant_id']
        user_id = event['body']['user_id']
        password = event['body']['password']
        
        # Verificar que el email y el password existen
        if user_id and password:
            # Hashea la contraseña antes de almacenarla
            hashed_password = hash_password(password)
            # Conectar DynamoDB
            dynamodb = boto3.resource('dynamodb')
            t_usuarios = dynamodb.Table('pf_usuarios')
            # Almacena los datos del user en la tabla de usuarios en DynamoDB
            usuario = {
                'tenant_id': tenant_id,
                'user_id': user_id,
                'password': hashed_password
            }
            response = t_usuarios.put_item(Item=usuario)
            # Retornar un código de estado HTTP 200 (OK) y un mensaje de éxito
            mensaje = {
                'message': 'User registered successfully',
                'user_id': user_id
            }
            print(usuario)
            return {
                'statusCode': 200,
                'body': mensaje,
                'response': response
            }
        else:
            mensaje = {
                'error': 'Invalid request body: missing tenant_id or user_id or password'
            }
            return {
                'statusCode': 400,
                'body': mensaje
            }

    except Exception as e:
        # Excepción y retornar un código de error HTTP 500
        print("Exception:", str(e))
        mensaje = {
            'error': str(e)
        }        
        return {
            'statusCode': 500,
            'body': mensaje
        }
