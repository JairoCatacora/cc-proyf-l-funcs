const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();

exports.handler = async (event) => {
    const { tenant_id, product_id } = event.pathParameters;

    const params = {
        TableName: 't_inventarios',
        Key: { tenant_id, product_id }
    };

    await dynamodb.delete(params).promise();

    return {
        statusCode: 200,
        body: JSON.stringify({
            message: 'Producto eliminado del inventario',
            tenant_id,
            product_id
        })
    };
};
