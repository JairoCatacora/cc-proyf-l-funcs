const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, PutCommand } = require("@aws-sdk/lib-dynamodb");
const { verifyProductExistence } = require("./verifyProductExistence"); // Importar la función

const client = new DynamoDBClient({});
const dynamo = DynamoDBDocumentClient.from(client);

const https = require('https');

const validateToken = (token) => {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'i1w2t4axo8.execute-api.us-east-1.amazonaws.com',
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

async function verifyProductExistence(tenant_id, product_id, product_name) {
  if (!tenant_id) {
    throw new Error("tenant_id is required");
  }

  if (product_id) {
    const response = await dynamo.send(
      new GetCommand({
        TableName: "pf_productos",
        Key: { tenant_id, product_id },
      })
    );

    if (!response.Item) {
      throw new Error("Product not found");
    }
    return response.Item;
  }

  if (product_name) {
    const response = await dynamo.send(
      new ScanCommand({
        TableName: "pf_productos",
        FilterExpression: "tenant_id = :tenant_id AND product_name = :product_name",
        ExpressionAttributeValues: {
          ":tenant_id": tenant_id,
          ":product_name": product_name,
        },
      })
    );

    if (!response.Items || response.Items.length === 0) {
      throw new Error("Product not found");
    }
    return response.Items;
  }

  throw new Error("Either product_id or product_name must be provided");
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

    const inventoryData = typeof event.body === "string" ? JSON.parse(event.body) : event.body;
    const { tenant_id, product_id, inventory_id, stock, observaciones } = inventoryData;

    if (!tenant_id || !product_id || !inventory_id || stock === undefined) {
      return {
        statusCode: 400,
        body: { message: "Missing required fields" },
      };
    }

    await verifyProductExistence(tenant_id, product_id);

    const lastModification = new Date().toISOString();

    await dynamo.send(
      new PutCommand({
        TableName: "pf_inventarioprod",
        Item: {
          tenant_id: tenant_id,
          ip_id: `${inventory_id}#${product_id}`,
          inventory_id: inventory_id,
          product_id: product_id,
          stock: stock,
          last_modification: lastModification,
          observaciones: observaciones || null,
        },
      })
    );

    return {
      statusCode: 201,
      body: {
        message: "Inventory created successfully",
      },
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: {
        error: error.message || "An error occurred while creating the inventory",
      },
    };
  }
};
