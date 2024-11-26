const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, GetCommand, ScanCommand } = require("@aws-sdk/lib-dynamodb");

const client = new DynamoDBClient({});
const dynamo = DynamoDBDocumentClient.from(client);

exports.lambda_handler = async (event) => {
  try {
    const { tenant_id, product_id, product_name } = JSON.parse(event.body);

    if (!tenant_id) {
      return {
        statusCode: 400,
        body: JSON.stringify({ error: "tenant_id is required" }),
      };
    }

    if (product_id) {
      const params = {
        TableName: "t_productos",
        Key: { tenant_id, product_id },
      };

      const response = await dynamo.send(new GetCommand(params));

      if (response.Item) {
        return { statusCode: 200, body: JSON.stringify(response.Item) };
      } else {
        return { statusCode: 404, body: JSON.stringify({ error: "Product not found" }) };
      }
    } else if (product_name) {
      const params = {
        TableName: "t_productos",
        FilterExpression: "tenant_id = :tenant_id AND product_name = :product_name",
        ExpressionAttributeValues: {
          ":tenant_id": tenant_id,
          ":product_name": product_name,
        },
      };

      const response = await dynamo.send(new ScanCommand(params));

      if (response.Items.length > 0) {
        return { statusCode: 200, body: JSON.stringify(response.Items) };
      } else {
        return { statusCode: 404, body: JSON.stringify({ error: "Product not found" }) };
      }
    } else {
      return {
        statusCode: 400,
        body: JSON.stringify({ error: "Either product_id or product_name must be provided" }),
      };
    }
  } catch (error) {
    console.error(error);
    return {
      statusCode: 500,
      body: JSON.stringify({ message: "Internal server error", error: error.message }),
    };
  }
};
