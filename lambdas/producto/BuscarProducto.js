const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, GetCommand, ScanCommand } = require("@aws-sdk/lib-dynamodb");

const client = new DynamoDBClient({});
const dynamo = DynamoDBDocumentClient.from(client);

exports.lambda_handler = async (event) => {
  try {
    const body = typeof event.body === "string" ? JSON.parse(event.body) : event.body;
    const { tenant_id, product_id, product_name } = body;

    if (!tenant_id) {
      return {
        statusCode: 400,
        body: JSON.stringify({ error: "tenant_id is required" }),
      };
    }

    let response;
    if (product_id) {
      response = await dynamo.send(
        new GetCommand({
          TableName: "t_productos",
          Key: { tenant_id, product_id },
        })
      );
    } else if (product_name) {
      response = await dynamo.send(
        new ScanCommand({
          TableName: "t_productos",
          FilterExpression: "tenant_id = :tenant_id AND product_name = :product_name",
          ExpressionAttributeValues: {
            ":tenant_id": tenant_id,
            ":product_name": product_name,
          },
        })
      );
    }

    if (response.Items && response.Items.length > 0) {
      return {
        statusCode: 200,
        body: JSON.stringify(response.Items),
      };
    } else {
      return {
        statusCode: 404,
        body: JSON.stringify({ error: "Product not found" }),
      };
    }
  } catch (error) {
    console.error(error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: error.message || "An error occurred" }),
    };
  }
};
