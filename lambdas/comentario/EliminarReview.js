const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, DeleteCommand } = require("@aws-sdk/lib-dynamodb");

const client = new DynamoDBClient({});
const dynamo = DynamoDBDocumentClient.from(client);

exports.lambda_handler = async (event) => {
  try {
    const body = typeof event.body === "string" ? JSON.parse(event.body) : event.body;
    const { tenant_id, product_id, review_id } = body;

    if (!tenant_id || !product_id || !review_id) {
      return {
        statusCode: 400,
        body: { message: "tenant_id, product_id, and inventory_id are required" },
      };
    }

    await dynamo.send(
      new DeleteCommand({
        TableName: "pf_comentarios",
        Key: {
          tenant_id: tenant_id,
          pr_id: `${product_id}#${review_id}`,
        },
      })
    );

    return {
      statusCode: 200,
      body:{
        message: "Review eliminado exitosamente",
      },
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: {
        error: error.message, message: "Ocurrió un error al eliminar el review",
      },
    };
  }
};