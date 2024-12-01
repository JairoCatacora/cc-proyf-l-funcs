const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, UpdateCommand } = require("@aws-sdk/lib-dynamodb");
const https = require("https");

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
    const lastModification = new Date().toISOString();
    const {tenant_id, product_id, review_id, user_id, comentario, stars} = body

    if (!tenant_id || !product_id || !review_id || !user_id || comentario === undefined || stars === undefined) {
      return {
        statusCode: 400,
        body: { message: "Missing required fields" },
      };
    }

    const params = {
      TableName: "pf_comentario",
      Key: {
        tenant_id: tenant_id,
        pr_id: `${product_id}#${review_id}`,
      },
      UpdateExpression: `
        SET 
        comentario = :comentario,
        stars = :stars,
        last_modification = :last_modification
      `,
      ExpressionAttributeValues: {
        ":stars": Number(stars),
        ":comentario": comentario,
        ":last_modification": lastModification,
      },
      ReturnValues: "UPDATED_NEW",
    };

    const updateResponse = await dynamo.send(new UpdateCommand(params));

    return {
      statusCode: 200,
      body: {
        message: "Se actualizó el comentario existosamente",
        updatedAttributes: updateResponse.Attributes,
      },
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: {
        error: error.message || "An error occurred while updating the review",
      },
    };
  }
};
