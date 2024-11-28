const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, GetCommand } = require("@aws-sdk/lib-dynamodb");

const client = new DynamoDBClient({});
const dynamo = DynamoDBDocumentClient.from(client);

exports.lambda_handler = async (event) => {
  try {
    const tenant_id = event.query.tenant_id;
    const product_id = event.query.product_id;
    const inventory_id = event.query.inventory_id;

    if (!tenant_id || !product_id || !inventory_id) {
      return {
        statusCode: 400,
        body: {
          message : "tenant_id, product_id, and inventory_id are required" 
        }
      };
    }

    const response = await dynamo.send(
      new GetCommand({
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
        item: response.Item 
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
