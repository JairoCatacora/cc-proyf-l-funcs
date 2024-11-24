const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();

exports.lambda_handler = async (event) => {
    // Extract data from the request body
    const { tenant_id, user_id, timestamp } = JSON.parse(event.body);

    // Ensure all required fields are present
    if (!tenant_id || !user_id || !timestamp) {
        return {
            statusCode: 400,
            body: JSON.stringify({ error: 'Missing required fields' })
        };
    }

    // Prepare parameters for deleting the review
    const params = {
        TableName: 't_reviews',
        Key: {
            tenant_id,
            user_id,
            timestamp
        },
        ConditionExpression: 'attribute_exists(tenant_id) AND attribute_exists(user_id) AND attribute_exists(timestamp)'
    };

    try {
        // Delete the review from DynamoDB
        await dynamodb.delete(params).promise();
        return {
            statusCode: 200,
            body: JSON.stringify({ message: 'Review/Question deleted successfully' })
        };
    } catch (error) {
        // Handle any errors during the delete process
        return {
            statusCode: 500,
            body: JSON.stringify({ error: `Error deleting review: ${error.message}` })
        };
    }
};
