import boto3
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def lambda_handler(event, context):
    try:
        # Obtener la lista de usuarios desde el evento
        usuarios = event.get('usuarios')

        # Verificar si se proporcionó la lista de usuarios
        if not usuarios or not isinstance(usuarios, list):
            mensaje = {
                'error': 'Invalid request body: missing or invalid usuarios list'
            }
            return {
                'statusCode': 400,
                'body': mensaje
            }
        
        # Inicializar la conexión a DynamoDB
        dynamodb = boto3.resource('dynamodb')
        t_usuarios = dynamodb.Table('t_usuarios')
        
        # Lista para almacenar el resultado de cada registro
        resultados = []

        # Procesar cada usuario en la lista
        for usuario in usuarios:
            tenant_id = usuario.get('tenant_id')
            user_id = usuario.get('user_id')
            password = usuario.get('password')
            user_info = usuario.get('user_info')

            # Validar que todos los campos necesarios estén presentes
            if tenant_id and user_id and password and user_info:
                try:
                    # Encriptar el password
                    hashed_password = hash_password(password)

                    # Insertar el usuario en la tabla DynamoDB
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

                    # Añadir un mensaje de éxito para este usuario
                    resultados.append({
                        'tenant_id': tenant_id,
                        'user_id': user_id,
                        'message': 'User registered successfully'
                    })
                except Exception as e:
                    # Capturar errores específicos para cada usuario
                    resultados.append({
                        'tenant_id': tenant_id,
                        'user_id': user_id,
                        'error': str(e)
                    })
            else:
                # Si faltan datos, registrar un error
                resultados.append({
                    'tenant_id': tenant_id,
                    'user_id': user_id,
                    'error': 'Missing required fields'
                })

        # Devolver el resumen de resultados
        return {
            'statusCode': 200,
            'body': resultados
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
