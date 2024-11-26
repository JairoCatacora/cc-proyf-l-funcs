const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, DeleteCommand } = require("@aws-sdk/lib-dynamodb");

const client = new DynamoDBClient({});
const dynamo = DynamoDBDocumentClient.from(client);

exports.lambda_handler = async (event) => {
  try {
    const body = typeof event.body === "string" ? JSON.parse(event.body) : event.body;
    const { tenant_id, product_id } = body;

    if (!tenant_id || !product_id) {
      return {
        statusCode: 400,
        body: JSON.stringify({ message: "tenant_id and product_id are required" }),
      };
    }

    const params = {
      TableName: "t_productos",
      Key: { tenant_id, product_id },
    };

    await dynamo.send(new DeleteCommand(params));

    return {
      statusCode: 200,
      body: JSON.stringify({ message: "Product deleted successfully" }),
    };
  } catch (error) {
    console.error(error);
    return {
      statusCode: 500,
      body: JSON.stringify({ message: "Internal server error", error: error.message }),
    };
  }
};
