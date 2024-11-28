const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, DeleteCommand } = require("@aws-sdk/lib-dynamodb");

const client = new DynamoDBClient({});
const dynamo = DynamoDBDocumentClient.from(client);

exports.lambda_handler = async (event) => {
  try {
    const { tenant_id } = event.query.tenant_id;
    const { product_id } = event.query.product_id;
    const { inventory_id } = event.inventory_id;

    await dynamo.send(
      new DeleteCommand({
        TableName: "pf_inventario",
        Key: {
          tenant_id: tenant_id,
          ip_id: `${inventory_id}#${product_id}`,
        },
      })
    );

    return {
      statusCode: 200,
      body:{
        message: "Producto eliminado exitosamente del inventario",
      },
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: {
        error: error.message || "Ocurrió un error al eliminar el producto",
      },
    };
  }
};
