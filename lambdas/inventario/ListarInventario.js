const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, QueryCommand } = require("@aws-sdk/lib-dynamodb");

const client = new DynamoDBClient({});
const dynamo = DynamoDBDocumentClient.from(client);

exports.lambda_handler = async (event) => {
  try {
    const { tenant_id } = event.query.tenant_id;
    const { inventory_id } = event.query.inventory_id;

    const response = await dynamo.send(
      new QueryCommand({
        TableName: "pf_inventarios",
        IndexName: "tenant_id-inventory_id-index",
        KeyConditionExpression: "tenant_id = :tenant_id AND inventory_id = :inventory_id",
        ExpressionAttributeValues: {
          ":tenant_id": tenant_id,
          ":inventory_id": inventory_id,
        },
      })
    );

    return {
      statusCode: 200,
      body: {
        message: "Inventario listado exitosamente",
        items: response.Items || [],
      },
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: {
        error: error.message || "Ocurrió un error al listar el inventario",
      },
    };
  }
};
