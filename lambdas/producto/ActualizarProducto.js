const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, UpdateCommand } = require("@aws-sdk/lib-dynamodb");

const client = new DynamoDBClient({});
const dynamo = DynamoDBDocumentClient.from(client);

const https = require('https');

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
    const { tenant_id, product_id, product_name, product_brand, product_info, product_price } = body;

    if (!tenant_id || !product_id || !product_name || !product_brand || !product_price ) {
      return {
        statusCode: 400,
        body: JSON.stringify({ message: "Missing required fields" }),
      };
    }

    const params = {
      TableName: "pf_productos",
      Key: { tenant_id, product_id },
      UpdateExpression:
        "SET product_name = :name, product_brand = :brand, product_info = :info, product_price = :price",
      ExpressionAttributeValues: {
        ":name": product_name,
        ":brand": product_brand,
        ":info": product_info,
        ":price": Number(product_price),
      },
      ReturnValues: "UPDATED_NEW",
    };

    const response = await dynamo.send(new UpdateCommand(params));

    return {
      statusCode: 200,
      body:{
        message: "Product updated successfully",
        updatedAttributes: response.Attributes,
      },
    };
  } catch (error) {
    console.error(error);
    return {
      statusCode: 500,
      body: { message: "Internal server error", error: error.message },
    };
  }
};