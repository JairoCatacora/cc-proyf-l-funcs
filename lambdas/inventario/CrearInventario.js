const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, PutCommand } = require("@aws-sdk/lib-dynamodb");

const client = new DynamoDBClient({});
const dynamo = DynamoDBDocumentClient.from(client);

exports.lambda_handler = async (event) => {
  try {
    const body = typeof event.body === "string" ? JSON.parse(event.body) : event.body;
    const {tenant_id, inventory_id, inventory_name } = body;

    await dynamo.send(
      new PutCommand({
        TableName: "pf_inventarios",
        Item: {
          tenant_id: tenant_id,
          inventory_id: inventory_id,
          inventory_name: inventory_name || null,
        },
      })
    );

    return {
      statusCode: 201,
      body: {
        message: "Inventory created successfully",
      },
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: {
        error: error.message || "An error occurred while creating the inventory",
      },
    };
  }
};
