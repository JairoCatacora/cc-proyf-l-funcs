const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, QueryCommand } = require("@aws-sdk/lib-dynamodb");

const client = new DynamoDBClient({});
const dynamo = DynamoDBDocumentClient.from(client);

exports.lambda_handler = async (event) => {
  try {
    const { tenant_id } = event.query.tenant_id;
    const { product_id } = event.query.product_id;
    const { inventory_id } = event.inventory_id;

    const response = await dynamo.send(
      new QueryCommand({
        TableName: "pf_inventario",
        Key: {
          tenant_id: tenant_id,
          ip_id: `${inventory_id}#${product_id}`,
        },
      })
    );

    return {
      statusCode: 200,
      body:{
        message: "Inventory retrieved successfully",
        items: response.Items || [], 
      },
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: {
        error: error.message || "An error occurred while retrieving the inventory",
      },
    };
  }
};