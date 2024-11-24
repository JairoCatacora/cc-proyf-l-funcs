const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();

exports.lambda_handler = async (event) => {
    // Extract data from the request body
    const { tenant_id, user_id, product_id, timestamp, answer } = JSON.parse(event.body);

    // Ensure all required fields are present
    if (!tenant_id || !user_id || !timestamp || !answer) {
        return {
            statusCode: 400,
            body: JSON.stringify({ error: 'Missing required fields' })
        };
    }

    // Prepare parameters for updating the review
    const params = {
        TableName: 't_reviews',
        Key: {
            tenant_id,
            user_id,
            timestamp
        },
        UpdateExpression: 'SET answer = :answer, answertimestamp = :answertimestamp',
        ExpressionAttributeValues: {
            ':answer': answer,
            ':answertimestamp': new Date().toISOString()
        },
        ConditionExpression: 'attribute_exists(tenant_id) AND attribute_exists(user_id) AND attribute_exists(timestamp)',
        ReturnValues: 'UPDATED_NEW'
    };

    try {
        // Update the review in DynamoDB
        const result = await dynamodb.update(params).promise();
        return {
            statusCode: 200,
            body: JSON.stringify({
                message: 'Review/Question answered successfully',
                updatedAttributes: result.Attributes
            })
        };
    } catch (error) {
        // Handle any errors during the update process
        return {
            statusCode: 500,
            body: JSON.stringify({ error: `Error answering review: ${error.message}` })
        };
    }
};
