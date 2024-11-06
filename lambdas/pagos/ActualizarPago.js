const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();

exports.lambda_handler = async (event) => {
    const { tenant_id, pago_id, pago_info } = JSON.parse(event.body);

    const params = {
        TableName: 't_pagos',
        Key: {
            'tenant_id': tenant_id,
            'pago_id': pago_id
        },
        UpdateExpression: 'SET pago_info = :info',
        ExpressionAttributeValues: {
            ':info': pago_info
        },
        ReturnValues: 'UPDATED_NEW'
    };

    const response = await dynamodb.update(params).promise();
    return {
        statusCode: 200,
        body: JSON.stringify({ message: 'Pago updated successfully', updatedAttributes: response.Attributes })
    };
};
