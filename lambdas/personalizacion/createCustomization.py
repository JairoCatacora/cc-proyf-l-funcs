import boto3
import json

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('t_customizations')

    customization_data = json.loads(event['body'])

    try:
        table.put_item(Item=customization_data)

        return {
            'statusCode': 201,
            'body': json.dumps({'message': 'Personalizacion creada correctamente'})
        }
    except Exception as e:
        print(str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
