const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, QueryCommand } = require("@aws-sdk/lib-dynamodb");

const client = new DynamoDBClient({});
const dynamo = DynamoDBDocumentClient.from(client);

exports.handler = async (event) => {
  try {
    const tenant_id = event.queryStringParameters.tenant_id;

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

    if (response.Items && response.Items.length > 0) {
      return {
        statusCode: 200,
        body: JSON.stringify(response.Items),
      };
    } else {
      return {
        statusCode: 404,
        body: JSON.stringify({ message: "No products found for the given tenant_id" }),
      };
    }
  } catch (error) {
    console.error(error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: error.message || "An error occurred while listing the products" }),
    };
  }
};