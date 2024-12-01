const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, PutCommand } = require("@aws-sdk/lib-dynamodb");

const client = new DynamoDBClient({});
const dynamo = DynamoDBDocumentClient.from(client);

const validateToken = (token) => {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: '0w7xbgvz6f.execute-api.us-east-1.amazonaws.com',
      path: '/test/token/validate',
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
    const {tenant_id, inventory_id, inventory_name } = body;

    await dynamo.send(
      new PutCommand({
        TableName: "pf_inventarios",
        Item: {
          tenant_id: tenant_id,
          inventory_id: inventory_id,
          inventory_name: inventory_name || null,
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
