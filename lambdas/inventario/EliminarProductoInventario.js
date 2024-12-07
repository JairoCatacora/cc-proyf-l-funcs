const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, DeleteCommand } = require("@aws-sdk/lib-dynamodb");

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
    const { tenant_id, product_id, inventory_id } = body;

    if (!tenant_id || !product_id || !inventory_id) {
      return {
        statusCode: 400,
        body: { message: "tenant_id, product_id, and inventory_id are required" },
      };
    }

    await dynamo.send(
      new DeleteCommand({
        TableName: "pf_inventarioprod",
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
        error: error.message, message: "Ocurrió un error al eliminar el producto",
      },
    };
  }
};