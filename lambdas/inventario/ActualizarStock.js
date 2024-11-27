const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, UpdateCommand } = require("@aws-sdk/lib-dynamodb");

const client = new DynamoDBClient({});
const dynamo = DynamoDBDocumentClient.from(client);

exports.lambda_handler = async (event) => {
  try {
    const inventoryData = typeof event.body === "string" ? JSON.parse(event.body) : event.body;

    await dynamo.send(
      new UpdateCommand({
        TableName: "pf_inventarios",
        Key: {
          inventory_id: inventoryData.inventory_id,
          tenant_id: inventoryData.tenant_id,
        },
        UpdateExpression: `
          SET 
            product_id = if_not_exists(product_id, :product_id),
            stock = if_not_exists(stock, :new_stock) + :new_stock,
            location = :location
        `,
        ExpressionAttributeValues: {
          ":product_id": inventoryData.product_id,
          ":new_stock": inventoryData.stock,
          ":location": inventoryData.location,
        },
      })
    );

    return {
      statusCode: 200,
      body: JSON.stringify({
        message: "Product added/updated in inventory successfully",
      }),
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({
        error: error.message || "An error occurred while updating the inventory",
      }),
    };
  }
};