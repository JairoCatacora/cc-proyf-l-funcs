import base64
import boto3

s3_client = boto3.client('s3')
BUCKET_NAME = 'prod-multishop-logos'

def lambda_handler(event, context):
    try:
        body = event['body']
        file_name = body['file_name']
        base_64_str = body['base_64_str']

        # Decodificar Base64 y subir a S3 con ACL publico
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=file_name,
            Body=base64.b64decode(base_64_str),
            ACL='public-read',
            ContentType='image/svg+xml'  # Ajustar esto si llegamos a usar otros formatos como PNG o JPG
        )

        file_url = f'https://{BUCKET_NAME}.s3.us-east-1.amazonaws.com/{file_name}'

        return {
            'statusCode': 200,
            'body': f'Se subio el logo correctamente. ({file_url})'
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Error al subir el logo: {str(e)}'
        }
