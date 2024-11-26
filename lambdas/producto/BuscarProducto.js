const { DynamoDBDocumentClient, GetCommand, ScanCommand } = require("@aws-sdk/lib-dynamodb");

exports.lambda_handler = async (event) => {
  try {
    const dynamo = DynamoDBDocumentClient.from(new DynamoDBClient({}));
    const { tenant_id, product_id, product_name } = event.queryStringParameters || {};

    if (!tenant_id) {
      return {
        statusCode: 400,
        body: JSON.stringify({ error: "tenant_id is required" }),
      };
    }

    if (product_id) {
      const response = await dynamo.send(
        new GetCommand({
          TableName: "t_productos",
          Key: { tenant_id, product_id },
        })
      );

      if (response.Item) {
        return {
          statusCode: 200,
          body: JSON.stringify(response.Item),
        };
      } else {
        return {
          statusCode: 404,
          body: JSON.stringify({ error: "Product not found" }),
        };
      }
    }

    if (product_name) {
      const response = await dynamo.send(
        new ScanCommand({
          TableName: "t_productos",
          FilterExpression: "tenant_id = :tenant_id AND product_name = :product_name",
          ExpressionAttributeValues: {
            ":tenant_id": tenant_id,
            ":product_name": product_name,
          },
        })
      );

      if (response.Items && response.Items.length > 0) {
        return {
          statusCode: 200,
          body: JSON.stringify(response.Items),
        };
      } else {
        return {
          statusCode: 404,
          body: JSON.stringify({ error: "Product not found" }),
        };
      }
    }

    return {
      statusCode: 400,
      body: JSON.stringify({ error: "Either product_id or product_name must be provided" }),
    };
  } catch (error) {
    console.error(error);
    return {
      statusCode: 500,
      body: JSON.stringify({ message: "Internal server error", error: error.message }),
    };
  }
};
