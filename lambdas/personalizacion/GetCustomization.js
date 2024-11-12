const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();

exports.handler = async (event) => {
    const { tenant_id } = event.pathParameters;

    const params = {
        TableName: 't_customizations',
        Key: { tenant_id }
    };

    try {
        const response = await dynamodb.get(params).promise();

        if (response.Item) {
            return {
                statusCode: 200,
                body: JSON.stringify(response.Item)
            };
        } else {
            return {
                statusCode: 404,
                body: JSON.stringify({ error: 'Las personalizaciones no fueron encontradas' })
            };
        }
    } catch (error) {
        console.error(error);
        return {
            statusCode: 500,
            body: JSON.stringify({ error: error.message })
        };
    }
};
