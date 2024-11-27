import boto3
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def lambda_handler(event, context):
    try:
        tenant_id = event['body']['tenant_id']
        user_id = event['body']['user_id']
        password = event['body']['password']
        username = event['body']['username']
        

        if user_id and password and username:

            hashed_password = hash_password(password)

            dynamodb = boto3.resource('dynamodb')
            t_usuarios = dynamodb.Table('pf_usuarios')

            usuario = {
                'tenant_id': tenant_id,
                'user_id': user_id,
                'password': hashed_password,
                'username': username
            }
            response = t_usuarios.put_item(Item=usuario)

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

        print("Exception:", str(e))
        mensaje = {
            'error': str(e)
        }        
        return {
            'statusCode': 500,
            'body': mensaje
        }
