const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, QueryCommand } = require("@aws-sdk/lib-dynamodb");

const client = new DynamoDBClient({});
const dynamo = DynamoDBDocumentClient.from(client);

exports.lambda_handler = async (event) => {
  try {
    const tenant_id = event.query.tenant_id;
    const inventory_id = event.query.inventory_id;

    if (!tenant_id || !inventory_id) {
      return {
        statusCode: 400,
        body: {
          message: "tenant_id and inventory_id are required"
        }
      };
    }

    const response = await dynamo.send(
      new QueryCommand({
        TableName: "pf_inventario",
        IndexName: "tenant_id-inventory_id-index",
        KeyConditionExpression: "tenant_id = :tenant_id AND inventory_id = :inventory_id",
        ExpressionAttributeValues: {
          ":tenant_id": tenant_id,
          ":inventory_id": inventory_id,
        },
      })
    );

    if (response.Items && response.Items.length > 0) {
      return {
        statusCode: 200,
        body: response.Items
      };
    } else {
      return {
        statusCode: 404,
        body: {
          message: "No inventory found"
        }
      };
    }
  } catch (error) {
    console.error(error);
    return {
      statusCode: 500,
      body: {
        error: error.message || "An error occurred while listing the inventory"
      }
    };
  }
};
