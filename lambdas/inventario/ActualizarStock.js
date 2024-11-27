const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();

exports.lambda_handler = async (event) => {
    const { tenant_id, product_id } = event.pathParameters;
    const { adjustment } = JSON.parse(event.body);
    if (!adjustment) {
        return {
            statusCode: 400,
            body: JSON.stringify({ error: 'Invalid request body: missing adjustment' })
        };
    }
    const paramsGet = {
        TableName: 't_inventarios',
        Key: { tenant_id, product_id }
    };
    const { Item } = await dynamodb.get(paramsGet).promise();
    if (!Item) {
        return {
            statusCode: 404,
            body: JSON.stringify({ error: 'Producto no fue encontrado en el inventario' })
        };
    }
    const newStock = Item.inventario_info.stock + adjustment;
    const newStatus = newStock > 0 ? 'available' : 'out_of_stock';
    const paramsUpdate = {
        TableName: 't_inventarios',
        Key: { tenant_id, product_id },
        UpdateExpression: 'SET inventario_info.stock = :stock, inventario_info.status = :status',
        ExpressionAttributeValues: {
            ':stock': newStock,
            ':status': newStatus
        },
        ReturnValues: 'UPDATED_NEW'
    };
    const result = await dynamodb.update(paramsUpdate).promise();
    return {
        statusCode: 200,
        body: JSON.stringify({
            message: 'Stock actualizado correctamente',
            updatedAttributes: result.Attributes
        })
    };
};