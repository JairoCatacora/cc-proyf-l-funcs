const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, UpdateCommand } = require("@aws-sdk/lib-dynamodb");
const axios = require("axios");

const client = new DynamoDBClient({});
const dynamo = DynamoDBDocumentClient.from(client);

exports.lambda_handler = async (event) => {
  try {
    const body = typeof event.body === "string" ? JSON.parse(event.body) : event.body;
    const lastModification = new Date().toISOString();
    const { tenant_id, inventory_id, product_id, cantidad, observaciones, add } = body;

    if (!tenant_id || !inventory_id || !product_id || cantidad === undefined || observaciones === undefined || add === undefined) {
      return {
        statusCode: 400,
        body: { message: "Missing required fields" },
      };
    }

    const apiUrl = `https://3j1d1u98t7.execute-api.us-east-1.amazonaws.com/dev/inventory/product?tenant_id=${tenant_id}&product_id=${product_id}&inventory_id=${inventory_id}`;
    const response = await axios.get(apiUrl);

    const currentStock = response.data?.stock;

    if (currentStock === undefined) {
      return {
        statusCode: 404,
        body: { message: "Item not found in inventory" },
      };
    }

    if (!add && currentStock < cantidad) {
      return {
        statusCode: 400,
        body: {
          message: "Insufficient stock to remove the requested quantity",
        },
      };
    }

    const params = {
      TableName: "pf_inventario",
      Key: {
        tenant_id: tenant_id,
        ip_id: `${inventory_id}#${product_id}`,
      },
      UpdateExpression: `
          SET 
          stock = stock ${add ? "+" : "-"} :cantidad,
          observaciones = :observaciones,
          last_modification = :last_modification
      `,
      ExpressionAttributeValues: {
        ":cantidad": Number(cantidad),
        ":observaciones": observaciones,
        ":last_modification": lastModification,
      },
      ReturnValues: "UPDATED_NEW",
    };

    const updateResponse = await dynamo.send(new UpdateCommand(params));

    return {
      statusCode: 200,
      body: {
        message: "Stock updated successfully",
        updatedAttributes: updateResponse.Attributes,
      },
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: {
        error: error.message || "An error occurred while updating the inventory",
      },
    };
  }
};