const { DynamoDBDocumentClient, QueryCommand } = require("@aws-sdk/lib-dynamodb");

exports.lambda_handler = async (event) => {
  try {
    const dynamo = DynamoDBDocumentClient.from(new DynamoDBClient({}));
    const { tenant_id } = event.queryStringParameters || {};

    if (!tenant_id) {
      return {
        statusCode: 400,
        body: JSON.stringify({ error: "tenant_id is required" }),
      };
    }

    const response = await dynamo.send(
      new QueryCommand({
        TableName: "t_productos",
        KeyConditionExpression: "tenant_id = :tenant_id",
        ExpressionAttributeValues: {
          ":tenant_id": tenant_id,
        },
      })
    );

    return {
      statusCode: 200,
      body: JSON.stringify(response.Items || []),
    };
  } catch (error) {
    console.error(error);
    return {
      statusCode: 500,
      body: JSON.stringify({ message: "Internal server error", error: error.message }),
    };
  }
};
