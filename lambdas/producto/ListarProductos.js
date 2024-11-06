const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();

exports.lambda_handler = async (event) => {
    const { tenant_id } = JSON.parse(event.body);

    const params = {
        TableName: 't_productos',
        KeyConditionExpression: 'tenant_id = :tenant_id',
        ExpressionAttributeValues: { ':tenant_id': tenant_id }
    };

    const response = await dynamodb.query(params).promise();
    return {
        statusCode: 200,
        body: JSON.stringify(response.Items.length ? response.Items : { message: 'No products found' })
    };
};
