const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, GetCommand, ScanCommand } = require("@aws-sdk/lib-dynamodb");

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

    const tenant_id = event.query.tenant_id;
    const product_id = event.query.product_id;
    const product_name = event.query.product_name;

    if (!tenant_id) {
      return {
        statusCode: 400,
        body: {
          message : "tenant_id is required" 
        }
      };
    }

    if (product_id) {
      const response = await dynamo.send(
        new GetCommand({
          TableName: "pf_productos",
          Key: { tenant_id, product_id },
        })
      );

      if (response.Item) {
        return {
          statusCode: 200,
          body: response.Item
        };
      } else {
        return {
          statusCode: 404,
          body: { 
            message: "Product not found" 
          }
        };
      }
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

      if (response.Items.length > 0) {
        return {
          statusCode: 200,
          body: response.Items
        };
      } else {
        return {
          statusCode: 404,
          body: { 
            message: "Product not found" 
          }
        };
      }
    }

    return {
      statusCode: 400,
      body: { 
        message: "Either product_id or product_name must be provided" 
      }
    };
  } catch (error) {
    console.error(error);
    return {
      statusCode: 500,
      body: { 
        error: error.message || "An error occurred while searching for the product" 
      }
    };
  }
};
