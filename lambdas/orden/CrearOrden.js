const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();

exports.lambda_handler = async (event) => {
    const { tenant_id, order_id, user_id, order_info } = JSON.parse(event.body);

    const params = {
        TableName: 't_orders',
        Item: {
            tenant_id,
            order_id,
            user_id,
            order_info
        }
    };

    await dynamodb.put(params).promise();
    return {
        statusCode: 201,
        body: JSON.stringify({ message: 'Order created successfully' })
    };
};