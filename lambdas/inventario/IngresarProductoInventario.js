const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, PutCommand } = require("@aws-sdk/lib-dynamodb");

const client = new DynamoDBClient({});
const dynamo = DynamoDBDocumentClient.from(client);

exports.lambda_handler = async (event) => {
  try {
    const inventoryData = typeof event.body === "string" ? JSON.parse(event.body) : event.body;

    const lastModification = new Date().toISOString();

    await dynamo.send(
      new PutCommand({
        TableName: "pf_inventarios",
        Item: {
          tenant_id: inventoryData.tenant_id,
          ip_id: `${inventoryData.inventory_id}#${inventoryData.product_id}`,
          inventory_id: inventoryData.inventory_id,
          product_id: inventoryData.product_id,
          stock: inventoryData.stock,
          last_modification: lastModification,
          observaciones: inventoryData.observaciones || null,
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
