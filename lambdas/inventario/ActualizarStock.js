const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, UpdateCommand } = require("@aws-sdk/lib-dynamodb");

const client = new DynamoDBClient({});
const dynamo = DynamoDBDocumentClient.from(client);

exports.lambda_handler = async (event) => {
  try {
    const inventoryData = typeof event.body === "string" ? JSON.parse(event.body) : event.body;

    const lastModification = new Date().toISOString();

    await dynamo.send(
      new UpdateCommand({
        TableName: "pf_inventario",
        Key: {
          tenant_id: inventoryData.tenant_id,
          ip_id: `${inventoryData.inventory_id}#${inventoryData.product_id}`,
        },
        UpdateExpression: `
          SET 
            stock = if_not_exists(stock, 0) + :new_stock,
            observaciones = :new_observaciones,
            last_modification = :last_modification
        `,
        ExpressionAttributeValues: {
          ":new_stock": inventoryData.stock,
          ":new_observaciones": inventoryData.observaciones || "",
          ":last_modification": lastModification,
        },
        ReturnValues: "UPDATED_NEW",
      })
    );

    return {
      statusCode: 200,
      body: {
        message: "Stock actualizado exitosamente",
      },
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: {
        error: error.message || "Ocurrió un error al actualizar el stock",
      },
    };
  }
};
