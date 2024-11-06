const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();

exports.lambda_handler = async (event) => {
    const { tenant_id, order_id } = JSON.parse(event.body);

    const params = {
        TableName: 't_orders',
        Key: {
            tenant_id,
            order_id
        }
    };

    const response = await dynamodb.get(params).promise();
    return {
        statusCode: 200,
        body: JSON.stringify(response.Item || { message: 'Order not found' })
    };
};
