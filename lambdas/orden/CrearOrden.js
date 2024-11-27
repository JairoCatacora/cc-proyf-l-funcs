const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, GetCommand, ScanCommand } = require("@aws-sdk/lib-dynamodb");

const client = new DynamoDBClient({});
const dynamo = DynamoDBDocumentClient.from(client);

exports.lambda_handler = async (event) => {
    tenant_id = event['body']['tenant_id']
    orden_id = event['body']['orden_id']
    user_id = event['body']['user_id']
    pago_id = event['body']['pago_amount']
    user_info = event['body']['user_info']
    productos_id = event['body']['productos_id']

    const { tenant_id, order_id, user_id, product_id, order_status } = JSON.parse(event.body);

    try {
        // Llamada al microservicio de pago para obtener la dirección y teléfono del usuario
        const userResponse = await axios.get(`https://api.example.com/users/${pago_id}`);
        const { user_address, user_phone } = userResponse.data;

        // Llamada al microservicio de productos para obtener información del producto
        const productResponse = await axios.get(`https://api.example.com/products/${product_id}`);
        const { product_name, product_price } = productResponse.data;

        // Conectar a DynamoDB y crear la orden
        const params = {
            TableName: 't_orders',
            Item: {
                tenant_id,
                order_id,
                user_id,
                user_address,
                user_phone,
                product_id,
                product_name,
                product_price,
                order_status,
                timestamp: new Date().toISOString() // Fecha y hora de creación de la orden
            }
        };

        // Guardar la orden en DynamoDB
        await dynamodb.put(params).promise();

        return {
            statusCode: 201,
            body: JSON.stringify({ message: 'Order created successfully' })
        };

    } catch (error) {
        return {
            statusCode: 500,
            body: JSON.stringify({ message: `Error creating order: ${error.message}` })
        };
    }
};
