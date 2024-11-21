const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();

exports.lambda_handler = async (event) => {
    try {
        // Obtener el cuerpo del evento y validar que sea un objeto
        const body = event.body;

        // Asegurarnos de que body y orders existen
        if (!body || !body.orders || !Array.isArray(body.orders)) {
            return {
                statusCode: 400,
                body: JSON.stringify({ error: 'Invalid request: missing or incorrect orders list' })
            };
        }

        const orders = body.orders;
        const tableName = 't_orders';
        const resultados = [];

        // Iterar sobre cada orden en la lista y guardarla en DynamoDB
        for (const order of orders) {
            const { tenant_id, order_id, user_id, order_info } = order;

            // Validar que todos los campos necesarios estén presentes
            if (!tenant_id || !order_id || !user_id || !order_info) {
                resultados.push({
                    order_id,
                    error: 'Missing required fields'
                });
                continue;
            }

            const params = {
                TableName: tableName,
                Item: {
                    tenant_id,
                    order_id,
                    user_id,
                    order_info
                }
            };

            try {
                // Insertar la orden en DynamoDB
                await dynamodb.put(params).promise();
                resultados.push({
                    tenant_id,
                    order_id,
                    message: 'Order created successfully'
                });
            } catch (error) {
                // Capturar errores específicos para cada orden
                resultados.push({
                    tenant_id,
                    order_id,
                    error: error.message
                });
            }
        }

        // Devolver el resumen de los resultados
        return {
            statusCode: 201,
            body: JSON.stringify(resultados)
        };

    } catch (error) {
        console.error('Exception:', error);
        return {
            statusCode: 500,
            body: JSON.stringify({ error: error.message })
        };
    }
};
