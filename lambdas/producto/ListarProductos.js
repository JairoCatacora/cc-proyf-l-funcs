const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, QueryCommand } = require("@aws-sdk/lib-dynamodb");

const client = new DynamoDBClient({});
const dynamo = DynamoDBDocumentClient.from(client);

exports.lambda_handler = async (event) => {
  try {
    const { tenant_id } = JSON.parse(event.body);

    if (!tenant_id) {
      return {
        statusCode: 400,
        body: JSON.stringify({ message: "tenant_id is required" }),
      };
    }

    const params = {
      TableName: "t_productos",
      KeyConditionExpression: "tenant_id = :tenant_id",
      ExpressionAttributeValues: { ":tenant_id": tenant_id },
    };

    const response = await dynamo.send(new QueryCommand(params));

    return {
      statusCode: 200,
      body: JSON.stringify(
        response.Items.length > 0 ? response.Items : { message: "No products found" }
      ),
    };
  } catch (error) {
    console.error(error);
    return {
      statusCode: 500,
      body: JSON.stringify({ message: "Internal server error", error: error.message }),
    };
  }
};
