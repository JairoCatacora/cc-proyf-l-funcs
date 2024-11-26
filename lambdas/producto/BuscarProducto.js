const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, GetCommand, ScanCommand } = require("@aws-sdk/lib-dynamodb");

const client = new DynamoDBClient({});
const dynamo = DynamoDBDocumentClient.from(client);

exports.lambda_handler = async (event) => {
  try {
    const tenant_id = event.query.tenant_id;
    const product_id = event.query.product_id;
    const product_name = event.query.product_name;

    if (!tenant_id) {
      return {
        statusCode: 400,
        body: {
          message : "tenant_id is required" 
        }
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
          body: result.Item
        };
      } else {
        return {
          statusCode: 404,
          body: { 
            message: "Product not found" 
          }
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

      if (response.Items.length > 0) {
        return {
          statusCode: 200,
          body: response.Items
        };
      } else {
        return {
          statusCode: 404,
          body: { 
            message: "Product not found" 
          }
        };
      }
    }

    return {
      statusCode: 400,
      body: { 
        message: "Either product_id or product_name must be provided" 
      }
    };
  } catch (error) {
    console.error(error);
    return {
      statusCode: 500,
      body: { 
        error: error.message || "An error occurred while searching for the product" 
      }
    };
  }
};
