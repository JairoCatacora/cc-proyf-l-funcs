const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, GetCommand } = require("@aws-sdk/lib-dynamodb");

const client = new DynamoDBClient({});
const dynamo = DynamoDBDocumentClient.from(client);

exports.lambda_handler = async (event) => {
  try {
    const { inventory_id, tenant_id } = event.queryStringParameters;

    const response = await dynamo.send(
      new GetCommand({
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
        message: "Inventory retrieved successfully",
        inventory: response.Item || {},
      }),
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({
        error: error.message || "An error occurred while retrieving the inventory",
      }),
    };
  }
};
