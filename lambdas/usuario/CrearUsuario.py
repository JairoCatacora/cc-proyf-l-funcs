import boto3
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def lambda_handler(event, context):
    try:
        tenant_id = event.get('tenant_id')
        user_id = event.get('user_id')
        password = event.get('password')
        user_info = event.get('user_info')

        if tenant_id and user_id and password and user_info:
            hashed_password = hash_password(password)
            dynamodb = boto3.resource('dynamodb')
            t_usuarios = dynamodb.Table('t_usuarios')

            t_usuarios.put_item(
                Item={
                    'tenant_id': tenant_id,
                    'user_id': user_id,
                    'password': hashed_password,
                    'user_info': {
                        'name': user_info.get('name'),
                        'phone': user_info.get('phone'),
                        'address': user_info.get('address')
                    }
                }
            )

            mensaje = {
                'message': 'User registered successfully',
                'tenant_id': tenant_id,
                'user_id': user_id
            }
            return {
                'statusCode': 200,
                'body': mensaje
            }
        else:
            mensaje = {
                'error': 'Invalid request body: missing tenant_id, user_id, password, or user_info'
            }
            return {
                'statusCode': 400,
                'body': mensaje
            }

    except Exception as e:
        print("Exception:", str(e))
        mensaje = {
            'error': str(e)
        }
        return {
            'statusCode': 500,
            'body': mensaje
        }
