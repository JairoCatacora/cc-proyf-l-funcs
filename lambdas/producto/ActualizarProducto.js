const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();

exports.lambda_handler = async (event) => {
    const { tenant_id, producto_id, product_info } = JSON.parse(event.body);

    const params = {
        TableName: 't_productos',
        Key: { tenant_id, producto_id },
        UpdateExpression: 'SET product_info = :info',
        ExpressionAttributeValues: { ':info': product_info },
        ReturnValues: 'UPDATED_NEW'
    };

    const response = await dynamodb.update(params).promise();
    return {
        statusCode: 200,
        body: JSON.stringify({ message: 'Product updated', updatedAttributes: response.Attributes })
    };
};
