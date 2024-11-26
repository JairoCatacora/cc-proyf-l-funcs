const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, PutCommand } = require("@aws-sdk/lib-dynamodb");

const client = new DynamoDBClient({});
const dynamo = DynamoDBDocumentClient.from(client);

exports.lambda_handler = async (event) => {
  try {
    const productData = typeof event.body === "string" ? JSON.parse(event.body) : event.body;

    await dynamo.send(
      new PutCommand({
        TableName: "t_productos",
        Item: {
          tenant_id: productData.tenant_id,
          product_id: productData.product_id,
          product_name: productData.product_name,
          product_brand: productData.product_brand,
          product_info: productData.product_info,
          product_price: parseFloat(productData.product_price), 
          product_stock: parseInt(productData.product_stock, 10), 
        },
      })
    );

    return {
      statusCode: 201,
      body: JSON.stringify({
        message: "Product created successfully",
      }),
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({
        error: error.message || "An error occurred while creating the product",
      }),
    };
  }
};