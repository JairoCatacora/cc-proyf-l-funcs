const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, GetCommand } = require("@aws-sdk/lib-dynamodb");

const client = new DynamoDBClient({});
const dynamo = DynamoDBDocumentClient.from(client);

exports.lambda_handler = async (event) => {
  try {
    const { tenant_id } = event.query.tenant_id;
    const { product_id } = event.query.product_id;
    const { inventory_id } = event.inventory_id;

    const response = await dynamo.send(
      new GetCommand({
        TableName: "pf_inventarios",
        Key: {
          tenant_id: tenant_id,
          ip_id: `${inventory_id}#${product_id}`,
        },
      })
    );

    return {
      statusCode: 200,
      body: {
        message: "Producto encontrado exitosamente",
        item: response.Item || {},
      },
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: {
        error: error.message || "Ocurrió un error al obtener el producto",
      },
    };
  }
};
