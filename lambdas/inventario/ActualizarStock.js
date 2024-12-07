const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, GetCommand, UpdateCommand } = require("@aws-sdk/lib-dynamodb");

const client = new DynamoDBClient({});
const dynamo = DynamoDBDocumentClient.from(client);

const https = require('https');

const validateToken = (token) => {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'bfh1meojk2.execute-api.us-east-1.amazonaws.com',
      path: '/prod/token/validate',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`, 
      },
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => {
        data += chunk;
      });
      res.on('end', () => {
        const response = JSON.parse(data);
        if (res.statusCode === 200) {
          resolve(response); 
        } else {
          reject(new Error(response.error || 'Token no válido')); 
        }
      });
    });

    req.on('error', (e) => {
      reject(new Error(`Error en la validación del token: ${e.message}`));
    });

    req.end();
  });
};

async function getInventoryItem(tenant_id, inventory_id, product_id) {
  if (!tenant_id || !inventory_id || !product_id) {
    throw new Error("tenant_id, product_id, and inventory_id are required");
  }

  const response = await dynamo.send(
    new GetCommand({
      TableName: "pf_inventarioprod",
      Key: {
        tenant_id: tenant_id,
        ip_id: `${inventory_id}#${product_id}`,
      },
    })
  );

  if (!response.Item) {
    throw new Error("Item not found in inventory");
  }

  return response.Item;
}

exports.lambda_handler = async (event) => {
  try {
    const token = event.headers.Authorization?.split(' ')[1]; 
    if (!token) {
      return {
        statusCode: 400,
        body: { message: "Token is required" },
      };
    }

    try {
      await validateToken(token); 
    } catch (error) {
      return {
        statusCode: 403,
        body: { message: error.message },
      };
    }
    
    const body = typeof event.body === "string" ? JSON.parse(event.body) : event.body;
    const lastModification = new Date().toISOString();
    const { tenant_id, inventory_id, product_id, cantidad, observaciones, add } = body;

    if (!tenant_id || !inventory_id || !product_id || cantidad === undefined || observaciones === undefined || add === undefined) {
      return {
        statusCode: 400,
        body: { message: "Missing required fields" },
      };
    }

    const currentItem = await getInventoryItem(tenant_id, inventory_id, product_id);
    const currentStock = currentItem.stock;

    if (!add && currentStock < cantidad) {
      return {
        statusCode: 400,
        body: {
          message: "Insufficient stock to remove the requested quantity",
        },
      };
    }

    const params = {
      TableName: "pf_inventarioprod",
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