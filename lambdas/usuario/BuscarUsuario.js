const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();

exports.lambda_handler = async (event) => {
    try {
        const { tenant_id, user_id } = event;

        if (tenant_id && user_id) {
            const params = {
                TableName: 't_usuarios',
                Key: {
                    tenant_id: tenant_id,
                    user_id: user_id
                }
            };

            const response = await dynamodb.get(params).promise();

            if (response.Item) {
                return {
                    statusCode: 200,
                    body: JSON.stringify({
                        message: 'User found',
                        user_data: response.Item
                    })
                };
            } else {
                return {
                    statusCode: 404,
                    body: JSON.stringify({
                        error: 'User not found'
                    })
                };
            }
        } else {
            return {
                statusCode: 400,
                body: JSON.stringify({
                    error: 'Invalid request body: missing tenant_id or user_id'
                })
            };
        }
    } catch (error) {
        console.error("Exception:", error);
        return {
            statusCode: 500,
            body: JSON.stringify({
                error: error.message
            })
        };
    }
};
