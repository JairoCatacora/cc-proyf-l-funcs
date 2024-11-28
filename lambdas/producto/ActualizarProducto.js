const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, UpdateCommand } = require("@aws-sdk/lib-dynamodb");

const client = new DynamoDBClient({});
const dynamo = DynamoDBDocumentClient.from(client);

exports.lambda_handler = async (event) => {
  try {
    const body = typeof event.body === "string" ? JSON.parse(event.body) : event.body;
    const { tenant_id, product_id, product_name, product_brand, product_info, product_price } = body;

    if (!tenant_id || !product_id || !product_name || !product_brand || !product_price ) {
      return {
        statusCode: 400,
        body: JSON.stringify({ message: "Missing required fields" }),
      };
    }

    const params = {
      TableName: "pf_productos",
      Key: { tenant_id, product_id },
      UpdateExpression:
        "SET product_name = :name, product_brand = :brand, product_info = :info, product_price = :price",
      ExpressionAttributeValues: {
        ":name": product_name,
        ":brand": product_brand,
        ":info": product_info,
        ":price": Number(product_price),
      },
      ReturnValues: "UPDATED_NEW",
    };

    const response = await dynamo.send(new UpdateCommand(params));

    return {
      statusCode: 200,
      body:{
        message: "Product updated successfully",
        updatedAttributes: response.Attributes,
      },
    };
  } catch (error) {
    console.error(error);
    return {
      statusCode: 500,
      body: { message: "Internal server error", error: error.message },
    };
  }
};