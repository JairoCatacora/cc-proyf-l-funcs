const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, QueryCommand } = require("@aws-sdk/lib-dynamodb");

const client = new DynamoDBClient({});
const dynamo = DynamoDBDocumentClient.from(client);

exports.lambda_handler = async (event) => {
  try {
    const tenant_id = event.query.tenant_id;
    const user_id = event.query.user_id;
    const product_id = event.query.product_id;

    if (!tenant_id || !user_id || product_id) {
      return {
        statusCode: 400,
        body: {
          message: "tenant_id, product_id, and inventory_id are required"
        }
      };
    }

    const response = await dynamo.send(
      new QueryCommand({
        TableName: "pf_comentarios",
        IndexName: "user_id-tp_id-index",
        KeyConditionExpression: "user_id = :user_id AND tp_id = :tp_id",
        ExpressionAttributeValues: {
          ":user_id": user_id,
          ":tp_id": `${tenant_id}#${product_id}`,
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
