const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();

exports.lambda_handler = async (event) => {
    const { tenant_id, producto_id } = JSON.parse(event.body);

    const params = {
        TableName: 't_productos',
        Key: { tenant_id, producto_id }
    };

    await dynamodb.delete(params).promise();
    return {
        statusCode: 200,
        body: JSON.stringify({ message: 'Product deleted' })
    };
};
