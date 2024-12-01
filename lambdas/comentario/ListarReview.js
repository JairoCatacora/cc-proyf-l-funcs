const https = require("https");
const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, QueryCommand } = require("@aws-sdk/lib-dynamodb");

const client = new DynamoDBClient({});
const dynamo = DynamoDBDocumentClient.from(client);

const validateToken = (token) => {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: "0w7xbgvz6f.execute-api.us-east-1.amazonaws.com",
      path: "/test/token/validate",
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    };

    const req = https.request(options, (res) => {
      let data = "";
      res.on("data", (chunk) => {
        data += chunk;
      });

      res.on("end", () => {
        try {
          const parsedData = JSON.parse(data);
          if (res.statusCode === 200) {
            resolve(parsedData);
          } else {
            reject(new Error(parsedData.message || "Invalid token"));
          }
        } catch (err) {
          reject(err);
        }
      });
    });

    req.on("error", (err) => {
      reject(err);
    });

    req.write({ token });
    req.end();
  });
};

exports.lambda_handler = async (event) => {
  try {
    const headers = event.headers || {};
    const authHeader = headers["Authorization"] || headers["authorization"];
    if (!authHeader || !authHeader.startsWith("Bearer ")) {
      return {
        statusCode: 400,
        body: { message: "Authorization header missing or invalid" },
      };
    }

    const token = authHeader.split(" ")[1];

    try {
      await validateToken(token);
    } catch (err) {
      return {
        statusCode: 403,
        body: { message: err.message || "Token validation failed" },
      };
    }

    const tenant_id = event.queryStringParameters?.tenant_id;
    const user_id = event.queryStringParameters?.user_id;

    if (!tenant_id || !user_id) {
      return {
        statusCode: 400,
        body: { message: "tenant_id and user_id are required" },
      };
    }

    const response = await dynamo.send(
      new QueryCommand({
        TableName: "pf_comentario",
        IndexName: "tenant_id-user_id-index",
        KeyConditionExpression: "tenant_id = :tenant_id AND user_id = :user_id",
        ExpressionAttributeValues: {
          ":tenant_id": tenant_id,
          ":user_id": user_id,
        },
      })
    );

    if (response.Items && response.Items.length > 0) {
      return {
        statusCode: 200,
        body: response.Items,
      };
    } else {
      return {
        statusCode: 404,
        body: { message: "No inventory found" },
      };
    }
  } catch (error) {
    console.error(error);
    return {
      statusCode: 500,
      body: {
        error: error.message || "An error occurred while processing the request",
      },
    };
  }
};
