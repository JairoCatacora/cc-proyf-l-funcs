const { DynamoDBDocumentClient, DeleteCommand } = require("@aws-sdk/lib-dynamodb");

exports.lambda_handler = async (event) => {
  try {
    const dynamo = DynamoDBDocumentClient.from(new DynamoDBClient({}));
    const { tenant_id, product_id } = JSON.parse(event.body);

    if (!tenant_id || !product_id) {
      return {
        statusCode: 400,
        body: JSON.stringify({ error: "tenant_id and product_id are required" }),
      };
    }

    await dynamo.send(
      new DeleteCommand({
        TableName: "t_productos",
        Key: { tenant_id, product_id },
      })
    );

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
