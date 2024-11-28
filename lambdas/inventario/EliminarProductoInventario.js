const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, DeleteCommand } = require("@aws-sdk/lib-dynamodb");

const client = new DynamoDBClient({});
const dynamo = DynamoDBDocumentClient.from(client);

exports.lambda_handler = async (event) => {
  try {
    const { inventory_id, tenant_id } = event.queryStringParameters;

    await dynamo.send(
      new DeleteCommand({
        TableName: "pf_inventarios",
        Key: {
          inventory_id: inventory_id,
          tenant_id: tenant_id,
        },
      })
    );

    return {
      statusCode: 200,
      body: JSON.stringify({
        message: "Product removed from inventory successfully",
      }),
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({
        error: error.message || "An error occurred while deleting the product from inventory",
      }),
    };
  }
}