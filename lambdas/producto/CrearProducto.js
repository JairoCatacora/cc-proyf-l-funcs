const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, PutCommand } = require("@aws-sdk/lib-dynamodb");

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

    const productData = typeof event.body === "string" ? JSON.parse(event.body) : event.body;

    await dynamo.send(
      new PutCommand({
        TableName: "pf_productos",
        Item: {
          tenant_id: productData.tenant_id,
          product_id: productData.product_id,
          product_name: productData.product_name,
          product_brand: productData.product_brand,
          product_info: productData.product_info,
          product_price: parseFloat(productData.product_price)
        },
      })
    );

    return {
      statusCode: 201,
      body: {
        message: "Product created successfully",
      },
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: {
        error: error.message || "An error occurred while creating the product",
      },
    };
  }
};