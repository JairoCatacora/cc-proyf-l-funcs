const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, PutCommand } = require("@aws-sdk/lib-dynamodb");

const client = new DynamoDBClient({});
const dynamo = DynamoDBDocumentClient.from(client);

exports.lambda_handler = async (event) => {
  try {
    const inventoryData = typeof event.body === "string" ? JSON.parse(event.body) : event.body;

    await dynamo.send(
      new PutCommand({
        TableName: "pf_inventarios",
        Item: {
          tenant_id: inventoryData.tenant_id,
          inventory_id: inventoryData.inventory_id,
          product_id: inventoryData.product_id,
          stock: inventoryData.stock,
          location: inventoryData.location,
        },
      })
    );

    return {
      statusCode: 201,
      body: JSON.stringify({
        message: "Inventory created successfully",
      }),
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({
        error: error.message || "An error occurred while creating the inventory",
      }),
    };
  }
};
